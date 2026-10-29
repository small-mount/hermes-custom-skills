"""Analyze media through an explicitly selected Gemini-native relay."""
import argparse
import base64
import json
import os
from pathlib import Path
import urllib.error
import urllib.request
import yaml


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--home', required=True, help='Active Hermes profile home')
    p.add_argument('--provider', default='namax-gemini',
                   help='Relay provider id (default: namax-gemini; beiluo-gemini lost its gemini models 2026-10-15, '
                        'myapi-gemini self-limits with 503 cpu-overloaded, zhongy-gemini disconnects on >45s slices)')
    p.add_argument('--key-env', default='NAMAX_GEMINI_API_KEY', help='Env var holding the relay key')
    p.add_argument('--model', default='gemini-3.8-flash')
    p.add_argument('--input', required=True)
    p.add_argument('--output', required=True)
    p.add_argument('--audio', action='store_true')
    a = p.parse_args()
    home = Path(a.home)
    cfg = yaml.safe_load((home / 'config.yaml').read_text(encoding='utf-8-sig'))
    provider = dict(cfg.get('providers', {}).get(a.provider) or {})
    if not provider:                        # list-slot profiles keep providers in custom_providers
        for entry in (cfg.get('custom_providers') or []):
            if entry.get('name') == a.provider:
                provider = dict(entry)
                break
    if not provider or not (provider.get('api') or provider.get('base_url')):
        p.error('provider %r not found in %s (checked providers + custom_providers)' % (a.provider, home))
    provider.setdefault('api', provider.get('base_url', ''))
    env = dict(os.environ)
    for line in (home / '.env').read_text(encoding='utf-8-sig').splitlines():
        if '=' in line and not line.lstrip().startswith('#'):
            k, v = line.split('=', 1)
            env.setdefault(k.strip(), v.strip().strip('\"\''))
    media = Path(a.input)
    if media.suffix.lower() not in ('.mp4', '.m4a'):
        p.error('This helper only supports mp4 video or m4a audio.')
    if media.stat().st_size > 20 * 1024 * 1024:
        p.error('Split media first: helper source-size cap is 20 MiB.')
    output = Path(a.output)
    if output.exists():
        p.error('Output already exists; choose a new evidence filename.')
    prompt = ('Transcribe only the attached audio verbatim in Chinese with mm:ss timestamps. Preserve names, numbers and uncertainties. No summary or external facts.' if a.audio else 'Research only the attached video and audio, in Chinese. Report observable duration and audio availability. Give timestamped sections, arguments, entities, URLs, commands, numbers and quotations. Distinguish spoken words, visible text and inference. If media is inaccessible say so; never invent content. Do not browse.')
    mime = 'audio/mp4' if a.audio else 'video/mp4'
    data = base64.b64encode(media.read_bytes()).decode('ascii')
    url = provider['api'].rstrip('/').removesuffix('/v1') + '/v1beta/models/' + a.model + ':generateContent'
    payload = {'contents': [{'role': 'user', 'parts': [{'text': prompt}, {'inlineData': {'mimeType': mime, 'data': data}}]}], 'generationConfig': {'maxOutputTokens': 16000, 'temperature': 0.1}}
    headers = {'Content-Type': 'application/json', **provider.get('extra_headers', {}), 'x-goog-api-key': env[a.key_env]}
    req = urllib.request.Request(url, data=json.dumps(payload).encode(), headers=headers)
    result = None
    for attempt in (1, 2, 3):               # 中转站 gemini 通道偶发 5xx（实测 myapi 503 抖动）→ 有限重试
        try:
            with urllib.request.urlopen(req, timeout=300) as r:
                result = json.load(r)
            break
        except urllib.error.HTTPError as e:
            body = e.read().decode('utf-8', 'replace')[:2000]
            result = {'http_error': e.code, 'body': body, 'attempt': attempt}
            if e.code < 500:
                break
        except Exception as e:
            result = {'error_type': type(e).__name__, 'detail': repr(e)[:300], 'attempt': attempt}
        if attempt < 3:
            import time as _t
            _t.sleep(3)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    candidates = result.get('candidates', [])
    text = '\n'.join(part.get('text', '') for cand in candidates for part in cand.get('content', {}).get('parts', []) if not part.get('thought'))
    print(text or json.dumps(result, ensure_ascii=False))
    print('usage:', result.get('usageMetadata'))
    return 0 if text else 1


if __name__ == '__main__':
    raise SystemExit(main())
