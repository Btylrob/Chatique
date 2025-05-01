<h1 align="center">Chatique</h1>

<p align="center">
  Real-time Telegram content moderation system powered by Roberta model.
</p>


<p align="center">
  <img src="media/demo.gif" alt="Demo GIF" width="800">
</p>

## Quick Start
![easysteps]()
1. Deploy on personal machine or docker
2. Select settings that match your associations needs
3. Press start

## Features & Uses - Everything is in real-time

### Live Profanity Filter

**Chatique moderates your groupchat in realtime to detect hate speach and profanity using fine-tuned data and Metas Roberta Model**

<p align="center">
  <img src="media/profanity.gif" alt="profanity">
</p>

### Sentence Transformers

**Use Sentence Transformers to capture input and compare to similar words in profanity filter**

<p align="center">
  <img src="media/sentencetransformer.git" alt="sentencetransformer">
</p>

### NSFW Image Detection

**Realtime NSFW image detection with custom in-house model**

<p align="center">
  <img src="media/NSFW.gif" alt="movie">
</p>

### Content Filtering

**Content moderation tools to manage users and set custom warnings such as 18+ emojis, urls, profanity, and hate speech**

<p align="center">
  <img src="media/content_filter.gif" alt="content_filter">
</p>

### Set Rules

**Create Your Own Rule-Book For Groupchat**

<p align="center">
  <img src="media/rules.gif" alt="rules" width="450"> 
  <br>
  <sub>null</sub>
</p>

### Omegle


## Installation (Manual)

**Please be aware that the installation requires technical skills and is not for beginners. Consider downloading the prebuilt version.**

### Installation

Chatique will work on a CPU but will run slower I reccomend to run on a machine that has CUDA compatible Nvidia GPU, however bot will still execute.

**1. Set up Your Platform**

-   Python (3.13 recommended)
-   pip
-   git
-   Telegram
-   Pyenv (Optional if on Linux Machine)

**2. Clone the Repository**

```bash
git clone https://github.com/Btylrob/Chatique.git
cd Chatique
```

**3. Add Your Telegram Bot Token**

1. [Telegram API Docs](https://core.telegram.org/)

Create a .env to load your token

**4. Install Dependencies**

We highly recommend using a `venv` to avoid issues.

For Windows:
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

**For macOS:**

Apple Silicon (M1/M2/M3) requires specific setup:

```bash
# Install Python 3.13 (specific version is important)
brew install python@3.13


# Create and activate virtual environment with Python 3.13
python3.13 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

** In case something goes wrong and you need to reinstall the virtual environment **

```bash
# Deactivate the virtual environment
rm -rf venv

# Reinstall the virtual environment
python -m venv venv
source venv/bin/activate

# install the dependencies again
pip install -r requirements.txt
```

**Run:** If you don't have a GPU, you can still run Chatique as it will default to your CPU


## Tips and Tricks

Check out these helpful guides to get the most out of Deep-Live-Cam:

- [Unlocking the Secrets to the Perfect Deepfake Image](https://deeplivecam.net/index.php/blog/tips-and-tricks/unlocking-the-secrets-to-the-perfect-deepfake-image) - Learn how to create the best deepfake with full head coverage
- [Video Call with DeepLiveCam](https://deeplivecam.net/index.php/blog/tips-and-tricks/video-call-with-deeplivecam) - Make your meetings livelier by using DeepLiveCam with OBS and meeting software
- [Have a Special Guest!](https://deeplivecam.net/index.php/blog/tips-and-tricks/have-a-special-guest) - Tutorial on how to use face mapping to add special guests to your stream
- [Watch Deepfake Movies in Realtime](https://deeplivecam.net/index.php/blog/tips-and-tricks/watch-deepfake-movies-in-realtime) - See yourself star in any video without processing the video
- [Better Quality without Sacrificing Speed](https://deeplivecam.net/index.php/blog/tips-and-tricks/better-quality-without-sacrificing-speed) - Tips for achieving better results without impacting performance
- [Instant Vtuber!](https://deeplivecam.net/index.php/blog/tips-and-tricks/instant-vtuber) - Create a new persona/vtuber easily using Metahuman Creator

Visit our [official blog](https://deeplivecam.net/index.php/blog/tips-and-tricks) for more tips and tutorials.


## Credits


-   All the people who starred or contributed to this repo 😍.

[![Stargazers](https://reporoster.com/stars/Btylrob/Chatique)](https://github.com/hacksider/Deep-Live-Cam/stargazers)



