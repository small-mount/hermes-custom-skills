# Hermes Custom Skills Collection

A collection of custom skills for [Hermes Agent](https://hermes-agent.nousresearch.com/) — an AI-powered development environment.

## 📦 Skills Included

### 🤖 Autonomous AI Agents
- **multi-agent-capability-adapter** — Compare and select external CLI agents for Hermes

### 🖥️ Desktop & System
- **edge-control** — Control, diagnose, and manage Microsoft Edge browser instances (CDP 9222, err32, junction fixes, login state management)
- **hermes-desktop-maintenance** — Clean restart and residual cleanup for Hermes desktop environment

### 📧 Email
- **personal-multi-account-email** — Multi-account email configuration for personal use

### 🎓 Learning & Education
- **learning-tracker** — Track learning progress and manage study materials
- **pastpapers-downloader** — Download and organize past examination papers

### 🎮 Minecraft
- **minecraft-client-to-server-conversion** — Convert Minecraft client-side mods to server-side implementations
- **relay-model-basic-probe** — Basic relay model testing and probing
- **shenshi-guixu** — 神识归墟 (Minecraft-related skill)

### 🎥 Media
- **video-content-research** — Research and analyze video content from Bilibili, YouTube, and local sources

## 🚀 Installation

### Using Hermes Skill Hub (Recommended)
```bash
# Coming soon: one-command installation via Hermes Skill Hub
```

### Manual Installation
1. Clone this repository:
```bash
cd $LOCALAPPDATA/hermes/skills
git clone https://github.com/small-mount/hermes-custom-skills.git
```

2. Symlink individual skills to your Hermes skills directory:
```bash
# Example: Install edge-control
ln -s hermes-custom-skills/edge-control ./edge-control
```

Or copy the skill directories directly into your Hermes skills folder.

## 📖 Usage

Each skill contains its own `SKILL.md` with:
- Description and use cases
- Installation requirements
- Usage instructions
- References and templates (if applicable)

To view a skill's documentation:
```bash
hermes skill view <skill-name>
```

## 🛠️ Requirements

- [Hermes Agent](https://hermes-agent.nousresearch.com/) v1.0+
- Additional dependencies are documented in each skill's `SKILL.md`

## 📝 Contributing

These skills are maintained for personal use but contributions and suggestions are welcome:

1. Fork this repository
2. Create a feature branch (`git checkout -b feature/amazing-skill`)
3. Commit your changes (`git commit -m 'Add amazing skill'`)
4. Push to the branch (`git push origin feature/amazing-skill`)
5. Open a Pull Request

## 📄 License

MIT License - see [LICENSE](LICENSE) for details

## 👤 Author

**Hill (大山)**
- GitHub: [@small-mount](https://github.com/small-mount)
- Email: 2523746088@qq.com

Created for use with Hermes Agent while studying A-Level Computer Science.

## 🙏 Acknowledgments

- [Hermes Agent](https://hermes-agent.nousresearch.com/) by Nous Research
- The Hermes community for inspiration and support

---

*These skills are provided as-is for educational and personal use. Always review and test skills before deploying them in production environments.*
