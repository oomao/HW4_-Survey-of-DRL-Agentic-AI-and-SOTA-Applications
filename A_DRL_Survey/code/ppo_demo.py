"""
HW4 Bonus MVP (B): Train a PPO agent on CartPole-v1 with Stable-Baselines3.

Goal: produce a reward learning curve that visually demonstrates RL training,
matching what we describe in Part 1 (PPO) and Part 6 (Comparative Analysis).

Run:
    python code/ppo_demo.py

Output:
    artifacts/ppo_cartpole_reward.png   — reward curve
    artifacts/ppo_cartpole_model.zip    — trained model
    artifacts/ppo_cartpole_log.txt      — training log
"""

from __future__ import annotations

import os
import time
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
import gymnasium as gym

from stable_baselines3 import PPO
from stable_baselines3.common.callbacks import BaseCallback
from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.evaluation import evaluate_policy
from stable_baselines3.common.monitor import Monitor


ARTIFACT_DIR = Path(__file__).resolve().parent.parent / "artifacts"
ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)


class EpisodeRewardLogger(BaseCallback):
    """Collects episode rewards from VecEnv Monitor wrappers."""

    def __init__(self):
        super().__init__()
        self.episode_rewards: list[float] = []
        self.episode_lengths: list[int] = []
        self.timesteps_at_episode: list[int] = []

    def _on_step(self) -> bool:
        infos = self.locals.get("infos", [])
        for info in infos:
            ep = info.get("episode")
            if ep is not None:
                self.episode_rewards.append(float(ep["r"]))
                self.episode_lengths.append(int(ep["l"]))
                self.timesteps_at_episode.append(int(self.num_timesteps))
        return True


def main():
    env_id = "CartPole-v1"
    total_timesteps = 50_000
    n_envs = 4
    seed = 42

    print(f"[ppo_demo] Building {n_envs}× VecEnv for {env_id} (seed={seed})")
    vec_env = make_vec_env(env_id, n_envs=n_envs, seed=seed, monitor_dir=str(ARTIFACT_DIR / "monitor"))

    print("[ppo_demo] Constructing PPO MlpPolicy …")
    model = PPO(
        policy="MlpPolicy",
        env=vec_env,
        learning_rate=3e-4,
        n_steps=128,
        batch_size=64,
        n_epochs=10,
        gamma=0.99,
        gae_lambda=0.95,
        clip_range=0.2,
        ent_coef=0.0,
        seed=seed,
        verbose=0,
    )

    cb = EpisodeRewardLogger()
    t0 = time.time()
    model.learn(total_timesteps=total_timesteps, callback=cb)
    elapsed = time.time() - t0
    print(f"[ppo_demo] Training done in {elapsed:.1f}s ({total_timesteps} env steps)")

    eval_env = Monitor(gym.make(env_id))
    mean_r, std_r = evaluate_policy(model, eval_env, n_eval_episodes=20, deterministic=True)
    print(f"[ppo_demo] Eval (20 episodes, deterministic): mean={mean_r:.1f} ± {std_r:.1f}")

    model_path = ARTIFACT_DIR / "ppo_cartpole_model.zip"
    model.save(model_path)
    print(f"[ppo_demo] Model saved → {model_path}")

    rewards = np.array(cb.episode_rewards)
    steps = np.array(cb.timesteps_at_episode)
    if len(rewards) == 0:
        print("[ppo_demo] WARNING: no episodes finished — try larger total_timesteps")
        return
    window = max(10, len(rewards) // 25)
    if len(rewards) >= window:
        smoothed = np.convolve(rewards, np.ones(window) / window, mode="valid")
        smoothed_steps = steps[window - 1:]
    else:
        smoothed = rewards
        smoothed_steps = steps

    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.plot(steps, rewards, color="#94a3b8", alpha=0.4, lw=1, label="per-episode reward")
    ax.plot(smoothed_steps, smoothed, color="#0ea5e9", lw=2.2, label=f"moving avg (window={window})")
    ax.axhline(500, color="#22c55e", lw=1, ls="--", alpha=0.7, label="CartPole-v1 max return = 500")
    ax.set_xlabel("env steps")
    ax.set_ylabel("episode return")
    ax.set_title(f"PPO on {env_id} — {len(rewards)} episodes, eval mean = {mean_r:.0f}")
    ax.set_ylim(0, 560)
    ax.legend(loc="lower right")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()

    out_path = ARTIFACT_DIR / "ppo_cartpole_reward.png"
    fig.savefig(out_path, dpi=140)
    plt.close(fig)
    print(f"[ppo_demo] Reward curve saved → {out_path}")

    log_path = ARTIFACT_DIR / "ppo_cartpole_log.txt"
    with open(log_path, "w", encoding="utf-8") as f:
        f.write(f"env_id           = {env_id}\n")
        f.write(f"total_timesteps  = {total_timesteps}\n")
        f.write(f"n_envs           = {n_envs}\n")
        f.write(f"seed             = {seed}\n")
        f.write(f"wallclock_sec    = {elapsed:.2f}\n")
        f.write(f"episodes         = {len(rewards)}\n")
        f.write(f"final_mean_eval  = {mean_r:.2f} ± {std_r:.2f}\n")
        f.write(f"max_episode_ret  = {rewards.max():.1f}\n")
    print(f"[ppo_demo] Log saved → {log_path}")


if __name__ == "__main__":
    main()
