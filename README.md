# 🧠 AI‑Powered Document Intelligence with Agentic RAG

[![Python Version](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python&logoColor=white)](#)
[![FastAPI](https://img.shields.io/badge/FastAPI-005571?logo=fastapi)](#)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?logo=streamlit&logoColor=white)](#)
[![ChromaDB](https://img.shields.io/badge/ChromaDB-Enabled-orange)](#)
[![License](https://img.shields.io/badge/License-MIT-green)](#)

> **An enterprise-grade document intelligence system that leverages agentic retrieval-augmented generation (RAG) to transform static files into an interactive, conversational knowledge engine.**

## 📖 Overview

A modern Generative AI application that transforms enterprise documents into an interactive knowledge system. Upload PDFs, spreadsheets, or text files and ask natural‑language questions. Behind the scenes, autonomous AI agents orchestrate document parsing, semantic retrieval, and LLM‑based reasoning to deliver accurate, grounded answers. Built with FastAPI, Streamlit, and a pluggable vector database layer for local or cloud deployment.

---

## ✨ Key Features

* 🤖 **Autonomous AI Agents:** Built-in agents for intelligent retrieval, step-by-step reasoning, and response validation.
* 🧩 **Modular RAG Pipeline:** Customizable ingestion pipeline handling document parsing, chunking, embedding, and semantic search.
* ⚡ **High-Performance Vector Store:** Pluggable local vector database powered by **ChromaDB** for ultra-fast, offline retrieval.
* 🔌 **Robust API Backend:** Fully documented, async-ready REST API served by **FastAPI**.
* 🖥️ **Interactive UI:** Clean, user-friendly frontend built with **Streamlit**.
* 🛡️ **Enterprise Guardrails:** Built-in safety mechanisms and governance rules for policy enforcement and audit logging.

---

## 🚀 Installation & Setup

You can run this project locally using a standard Python virtual environment or deploy it instantly using Docker.

### Option A: Run Locally (Without Docker)

**1. Clone the repository**
```bash
git clone <your-repo-url>
cd <your-repo-folder>
```
**2. Create and activate a virtual environment**
```bash
python3 -m venv venv

# macOS/Linux
source venv/bin/activate  

# Windows
venv\Scripts\activate
```
