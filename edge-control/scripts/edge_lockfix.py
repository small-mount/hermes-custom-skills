#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""edge_lockfix.py - release a stuck Chromium/Edge lockfile via Windows Restart Manager.

Symptom this fixes (2026-09-28 field case):
  - Edge launch fails: 'Lock file can not be created! Error code: 32'
    (ProcessSingleton create failure = another process holds <profile>/lockfile)
  - mv / rm of the lockfile fails: 'Device or resource busy' (sharing violation)
  - handle64.exe cannot see the holder -> holder is a higher-integrity/protected process

Method:
  1) Restart Manager RmGetList enumerates holder(s) of the lockfile (may be inaccessible:
     res=234 with needed=1 and empty detail is expected for protected processes).
  2) RmShutdown(graceful=0) asks the holder(s) to close; lockfile is then removed on exit.
  3) Verify: exclusive open + file existence; report final state.

Usage:
  python edge_lockfix.py [PROFILE_DIR]
  default PROFILE_DIR = %USERPROFILE%\\.openclaw\\tools\\xbrowser\\profiles\\edge

CAVEATS (read before running on a machine with live browsing sessions):
  - In the field case the operation succeeded but ALL msedge.exe windows of the
    machine (user instances included) exited shortly after. Notify the user first.
  - If RmShutdown returns non-zero, escalate (manual close / reboot) - do NOT loop-kill
    random processes, and never force-kill browsers you did not start.

Source: edge-control skill (same file as relay-evaluation-suite/scripts/edge_lockfix.py;
        keep the two in sync on edits).
"""
import ctypes
import os
import sys
import time
import uuid
from ctypes import wintypes

CCH_RM_MAX_APP_NAME = 255
CCH_RM_MAX_SVC_NAME = 63
CCH_RM_SESSION_KEY = 32

DEFAULT_DIR = os.path.join(os.path.expanduser('~'), '.openclaw', 'tools', 'xbrowser', 'profiles', 'edge')


class FILETIME(ctypes.Structure):
    _fields_ = [('dwLowDateTime', wintypes.DWORD), ('dwHighDateTime', wintypes.DWORD)]


class RM_UNIQUE_PROCESS(ctypes.Structure):
    _fields_ = [('dwProcessId', wintypes.DWORD), ('ProcessStartTime', FILETIME)]


class RM_PROCESS_INFO(ctypes.Structure):
    _fields_ = [
        ('Process', RM_UNIQUE_PROCESS),
        ('strAppName', wintypes.WCHAR * (CCH_RM_MAX_APP_NAME + 1)),
        ('strServiceShortName', wintypes.WCHAR * (CCH_RM_MAX_SVC_NAME + 1)),
        ('ApplicationType', wintypes.ULONG),
        ('AppStatus', wintypes.ULONG),
        ('TSSessionId', wintypes.DWORD),
        ('bRestartable', wintypes.BOOL),
    ]


def main():
    profile_dir = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_DIR
    lockfile = os.path.join(profile_dir, 'lockfile')
    print('profile dir:', profile_dir)
    print('lockfile   :', lockfile, '(exists: %s)' % os.path.exists(lockfile))

    rstrtmgr = ctypes.WinDLL('rstrtmgr')

    session = wintypes.DWORD()
    key = ctypes.create_unicode_buffer(CCH_RM_SESSION_KEY + 1)
    key.value = uuid.uuid4().hex
    res = rstrtmgr.RmStartSession(ctypes.byref(session), 0, key)
    print('RmStartSession res =', res)
    if res != 0:
        raise SystemExit(1)

    files = (wintypes.LPCWSTR * 1)(lockfile)
    res = rstrtmgr.RmRegisterResources(session.value, 1, files, 0, None, 0, None)
    print('RmRegisterResources res =', res)

    # 1) enumerate holders (informational)
    needed = wintypes.UINT(0)
    count = wintypes.UINT(0)
    reasons = wintypes.DWORD(0)
    res = rstrtmgr.RmGetList(session.value, ctypes.byref(needed), ctypes.byref(count), None, ctypes.byref(reasons))
    print('RmGetList: res =', res, 'holders needed =', needed.value)
    if needed.value:
        arr = (RM_PROCESS_INFO * needed.value)()
        cnt = wintypes.UINT(0)
        res2 = rstrtmgr.RmGetList(session.value, ctypes.byref(needed), ctypes.byref(cnt), arr, ctypes.byref(reasons))
        if res2 == 0 and cnt.value:
            for i in range(cnt.value):
                info = arr[i]
                print('  HOLDER: pid =', info.Process.dwProcessId, '| app =', info.strAppName)
        else:
            print('  (holder details unavailable: res=%d count=%d - protected process, expected)' % (res2, cnt.value))

    # 2) graceful shutdown request
    res = rstrtmgr.RmShutdown(session.value, 0, None)
    print('RmShutdown(graceful) res =', res)
    rstrtmgr.RmEndSession(session.value)

    # 3) verify
    time.sleep(2)
    if not os.path.exists(lockfile):
        print('RESULT: lockfile is GONE -> released/cleaned. Start the browser now.')
        return
    k32 = ctypes.windll.kernel32
    k32.CreateFileW.restype = wintypes.HANDLE
    h = k32.CreateFileW(lockfile, 0x80000000 | 0x40000000, 0, None, 3, 0, None)
    hval = h if isinstance(h, int) else ctypes.cast(h, ctypes.c_void_p).value
    if hval == ctypes.c_void_p(-1).value:
        print('RESULT: still held (exclusive open failed, err=%d). Escalate.' % k32.GetLastError())
    else:
        k32.CloseHandle(h)
        print('RESULT: exclusive open OK -> lock released but file remains; safe to delete if needed.')


if __name__ == '__main__':
    main()
