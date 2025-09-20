# BeSIM: A Benchmark for Evaluating the Interpretation of Social Interactions in Brazil Using Multimodal Large Language Models

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Code and data available at: https://github.com/M4Falcao/BeSIM**

This repository contains the code and data for **BeSIM**, a benchmark developed to evaluate the competence of Large Multimodal Language Models (MLLMs) in interpreting social interactions among Brazilians.

## About the Project

The rapid evolution of MLLMs has expanded the possibilities for automatically understanding complex real-world scenarios, yet their ability to interpret social interactions through video is still underexplored.

BeSIM (Benchmark for Social Interaction in Multimodal models) aims to fill this gap by providing a dataset and an evaluation methodology focused on social interactions within the Brazilian context. The benchmark is based on the APRACE taxonomy to categorize the core elements of social interaction.

## Methodology

### Dataset Collection and Structure

The BeSIM dataset consists of 45 videos collected from the YouTube platform, which generated 225 multiple-choice questions. The videos were selected to represent a wide diversity of contexts from the Brazilian reality, such as humor, interviews, and sporting events, in order to capture a variety of interactional dynamics.

**Video selection criteria:**
* Interactions featuring Brazilians.
* Published or recorded within the last 10 years.
* With a maximum duration of 600 seconds.
* Sourced exclusively from the YouTube platform.

The videos were organized into five main categories: knowledge, cinema and television, sports competition, artistic performance, and life logging.

### Question Formulation

Following the Video-MME methodology, multiple-choice questions were created with four alternatives, only one of which is correct. The questions were designed to assess the model's ability to:

* Recognize and interpret emotions from multiple verbal and non-verbal cues.
* Understand the interpersonal relationships of the participants.
* Identify the activities being performed and infer the underlying intentions.
* Interpret the environment in which the interaction occurs.
* Evaluate how the interaction unfolded, defining its valence and coherence.
* Demonstrate temporal reasoning regarding the evolution of the interaction.

The questions are classified according to the adapted APRACE taxonomy categories (Agents, Relation, Activity, Context, and Evaluation). To ensure objectivity, the answers must be derived exclusively from the data presented in the video, without reference to external knowledge.

## Results

The models were evaluated using accuracy as the primary metric. The results show that models like **Gemini 2.5 Pro** surpass their performance on generalist benchmarks, such as Video-MME, achieving up to **90% accuracy** on BeSIM. This indicates that MLLMs have great potential for interpreting human interactions when evaluated appropriately.

### Accuracy Table

The following table presents the accuracy of the evaluated models in each category of the adapted APRACE taxonomy.

| Model                       | Agents  | Relation | Activity | Context  | Evaluation | **Average** |
| :-------------------------- | :-----: | :------: | :------: | :------: | :--------: | :---------: |
| gemini-1.5-pro              | 86.36%  | 95.45%   | 86.36%   | 90.91%   | 68.18%     | **85.45%** |
| gemini-2.5-pro              | 90.91%  | 90.91%   | 95.45%   | 90.91%   | 81.82%     | **90.00%** |
| gemini-2.5-flash            | 77.27%  | 95.45%   | 95.45%   | 90.91%   | 77.27%     | **87.27%** |
| LLaVA-Video-7B-Qwen2 8fr    | 81.82%  | 86.36%   | 68.18%   | 63.64%   | 50.00%     | **70.00%** |
| **Average** | 84.09%  | 92.05%   | 86.36%   | 84.09%   | 69.32%     | **83.18%** |

### Conclusions

Despite the good overall performance, a significant drop in accuracy was identified across all models in the task of evaluating whether an interaction was pleasant or not. This result points to a limitation in interpreting the affective dimension of interactions, which requires attention, especially in sensitive applications such as detecting situations of violence or harassment.

## Citation

If you use BeSIM in your research, please cite our paper.

```bibtex
@inproceedings{falcao2024mllms,
  title={BeSIM: A Benchmark for Evaluating the Interpretation of Social Interactions in Brazil Using Multimodal Large Language Models},
  author={Falcão, Mateus Souza and dos Santos, Vitória Sofia Vieira and Simões, Francisco Paulo Magalhaes},
  year={2025}
}