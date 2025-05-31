# 🔒 LockIn — *Win the War Against Distraction*

> *“You’ll never change your life until you change something you do daily.”*
> — John C. Maxwell

Welcome to **LockIn** — not just another productivity app, but your personal shield in a digital world built to steal your time, your attention, and your focus.

If you’ve ever sat down to do deep work and found yourself on YouTube “just for 5 minutes,” you know the truth:
Distractions are no longer occasional — they’re systemic.

**LockIn is your rebellion.**

---

## 💥 What Is LockIn?

LockIn is a minimalist, local-first app that **blocks your digital noise** at the root. It’s your silent partner in building focus, flow, and fulfillment. With LockIn, you’re not asking your brain to “resist distraction” — you’re removing the temptation altogether.

No more extensions.
No more guilt.
No more broken promises to yourself.

Just **pure, uninterrupted time** to do the work that matters.

---

## 🧠 Why It Matters

We live in a world of infinite scroll, dopamine loops, and algorithmic distractions.
But your attention? That’s **finite**.

* The average knowledge worker switches tasks every 3 minutes.
* After each distraction, it takes \~23 minutes to fully refocus.
* You lose hours. Days. Weeks.

LockIn gives that time back to you.

---

## ✨ Key Features

| Feature                      | Why It Matters                                                                |
| ---------------------------- | ----------------------------------------------------------------------------- |
| 🔒 **True Website Blocking** | Blocks sites at the OS level — not just your browser. No loopholes. No mercy. |
| ⏱️ **Focus Session Engine**  | Structured deep work intervals with break logic to keep your brain sharp.     |
| 💬 **Motivational Fuel**     | Custom quotes that remind you *why* you started when your willpower dips.     |
| 🧘 **Simple, Local, Yours**  | No accounts, no cloud, no noise. Just a clean tool that respects your space.  |

---

## 🛠️ Setup in 2 Minutes

### 1. Clone It

```bash
git clone https://github.com/n0sh4d3/lockin-app.git
cd lockin-app
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Launch the Battle Station

```bash
python main.py
```

> 🛡️ For website blocking to work, you’ll need admin/root access. LockIn modifies your system’s `hosts` file — like a real productivity warrior.

---

## ⚙️ Customize It

### `sites.json` — What’s holding you back?

```json
[
  "instagram.com",
  "reddit.com",
  "netflix.com"
]
```

### `fokus_settings.json` — How do you work best?

```json
{
  "focus_duration_minutes": 50,
  "break_duration_minutes": 10,
  "enable_quotes": true
}
```

---

## 📁 File Breakdown

| File                  | Purpose                           |
| --------------------- | --------------------------------- |
| `main.py`             | Entry point of the app            |
| `websiteblocker.py`   | Blocks/unblocks distracting sites |
| `fokus.py`            | Manages timed sessions and breaks |
| `quotes.py`           | Delivers motivation during focus  |
| `settings_manager.py` | Handles settings loading/saving   |
| `sites.json`          | Your blacklist                    |
| `fokus_settings.json` | Session configuration             |
| `requirements.txt`    | Python dependencies               |

---

## 👊 Why LockIn Over Other Apps?

* 🧱 **Not a Chrome Extension** — Works system-wide. You can't just "open another browser."
* 🔐 **Fully Offline** — No data leaves your device. No ads. No tracking. No BS.
* 🚫 **No Gamification Gimmicks** — Just you and the work that matters.
* ✍️ **Hackable & Simple** — JSON-based config. Built in Python. Change it however you want.

---

## 🤝 Contribute to the Mission

Got an idea? Found a bug? Want to make this better for others like you?

* Fork the repo
* Make your move
* Submit a PR

Together, we can build something that helps people fight back against distraction and take their time seriously again.

---

## 🪪 License

This project is open-sourced under the [MIT License](LICENSE).
Use it. Change it. Share it. Just don’t let it sit idle.

---

## 🧭 Final Word

There’s no productivity hack that will save you if your attention is under siege.

**LockIn is not a silver bullet.**
It’s a tool — one built for those ready to take back control. To do the hard work. To show up for themselves, every damn day.

So go ahead. Block the noise.
Start the timer.
And **lock in**.


todo:
fix build process lol
