---
title: "A Survey of Deep Reinforcement Learning, Agentic AI, and State-of-the-Art Applications (2024–2026)"
subtitle: "Homework 4 — Survey Report"
author: "DRL Course, Student ID: csm088220"
date: "May 2026"
geometry: "a4paper, margin=2.2cm"
fontsize: 11pt
linkcolor: blue
toc: true
toc-depth: 2
numbersections: true
papersize: a4
header-includes:
  - \usepackage{booktabs}
  - \usepackage{longtable}
  - \usepackage{xcolor}
  - \usepackage{graphicx}
---

\begin{abstract}
\noindent Deep Reinforcement Learning (DRL) has evolved from a research curiosity capable of mastering Atari games into a foundational ingredient of today's most capable AI systems — from humanoid robots fluently manipulating household objects, to LLM-powered agents that browse the web, write code, and conduct multi-step scientific reasoning. This report surveys the DRL landscape across three axes: (1) the algorithmic foundations from DQN to Decision Transformer; (2) the simulation platforms and open-source ecosystem that enable modern DRL research; and (3) the rise of \emph{agentic AI} — large-model agents that combine RL fine-tuning (RLHF/RLAIF/RLVR) with tool use, planning, and embodiment. We analyze representative SOTA systems from 2024–2026 across robotics, game AI, and AI for science, identify five cross-cutting research trends (world models, diffusion policies, foundation agents, sim2real, RL+Transformers), and provide a comparative analysis of five algorithm families along axes of sample efficiency, stability, and real-world deployability. A small reproducible Bonus MVP — a PPO agent on classic control plus a tool-using LLM agent — is included to make the survey concrete.
\end{abstract}

\vspace{0.5em}
\noindent\textbf{Keywords:} Deep Reinforcement Learning, Agentic AI, RLHF, RLAIF, Vision-Language-Action Models, Diffusion Policy, World Models, Foundation Agents, Sim2Real.

\newpage
