# BeSIM: Um Benchmark para Avaliação de Interações Sociais por MLLMs

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Código e dados disponíveis em: https://github.com/M4Falcao/BeSIM**

Este repositório contém o código e os dados do **BeSIM**, um benchmark desenvolvido para avaliar a competência de Modelos Multimodais de Linguagem em Larga Escala (MLLMs) na interpretação de interações sociais entre brasileiros.

## Sobre o Projeto

A rápida evolução dos MLLMs tem ampliado as possibilidades de compreensão automática de cenários complexos do mundo real, porém sua capacidade de interpretar interações sociais por meio de vídeos ainda é pouco explorada.

O BeSIM (Benchmark for Social Interaction in Multimodal models) busca preencher essa lacuna, fornecendo um conjunto de dados e uma metodologia de avaliação focada em interações sociais no contexto brasileiro. O benchmark é fundamentado na taxonomia APRACE para categorizar os elementos centrais da interação social.

## Metodologia

### Coleta e Estrutura do Dataset

O dataset do BeSIM é composto por 45 vídeos coletados da plataforma YouTube, que originaram 225 questões de múltipla escolha. Os vídeos foram selecionados para representar uma ampla diversidade de contextos da realidade brasileira, como humor, entrevistas e eventos esportivos, a fim de capturar uma variedade de dinâmicas interacionais.

**Critérios de seleção dos vídeos:**
* Interações protagonizadas por brasileiros.
* Publicados ou registrados nos últimos 10 anos.
* Com duração máxima de 600 segundos.
* Provenientes exclusivamente da plataforma YouTube.

Os vídeos foram organizados em cinco categorias principais: conhecimento, cinema e televisão, competição esportiva, performance artística e registro de vida.

### Formulação das Questões

Seguindo a metodologia do Video-MME, foram elaboradas questões de múltipla escolha com quatro alternativas, sendo apenas uma correta. As perguntas foram criadas para avaliar a capacidade do modelo em:

* Reconhecer e interpretar emoções a partir de múltiplas pistas verbais e não verbais.
* Compreender as relações interpessoais dos participantes.
* Identificar as atividades realizadas e inferir as intenções subjacentes.
* Interpretar o ambiente no qual a interação ocorre.
* Avaliar a forma como a interação se deu, definindo sua valência e coerência.
* Apresentar raciocínio temporal a respeito da evolução da interação.

As questões são classificadas de acordo com as categorias da taxonomia APRACE adaptada (Agentes, Relação, Atividade, Contexto e Avaliação). Para garantir a objetividade, as respostas devem ser obtidas exclusivamente a partir dos dados apresentados no vídeo, sem referência a conhecimento externo.

## Resultados

Os modelos foram avaliados utilizando a acurácia como métrica principal. Os resultados demonstram que modelos como o **Gemini 2.5 Pro** superam seu desempenho em benchmarks generalistas, como o Video-MME, alcançando até **90% de acurácia** no BeSIM. Isso indica que os MLLMs apresentam grande potencial na interpretação de interações humanas quando avaliados adequadamente.

### Tabela de Acurácia

A tabela a seguir apresenta a acurácia dos modelos avaliados em cada categoria da taxonomia APRACE adaptada.

| Modelo | Agentes | Relação | Atividade | Contexto | Avaliação | **Média** |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| gemini-1.5-pro | 86.36% | 95,45% | 86,36% | 90,91% | 68,18% | **85,45%** |
| gemini-2.5-pro | 90,91% | 90,91% | 95,45% | 90,91% | 81,82% | **90,00%** |
| gemini-2.5-flash | 77,27% | 95.45% | 95,45% | 90,91% | 77,27% | **87,27%** |
| LLaVA-Video-7B-Qwen2 8fr | 81,82% | 86,36% | 68,18% | 63,64% | 50,00% | **70,00%** |
| **Média** | 84,09% | 92,05% | 86,36% | 84,09% | 69,32% | **83,18%** |

### Conclusões

Apesar do bom desempenho geral, foi identificada uma queda significativa na acurácia em todos os modelos na tarefa de avaliar se a interação foi agradável ou não. Esse resultado aponta para uma limitação na interpretação da dimensão afetiva das interações, o que exige atenção, sobretudo em aplicações sensíveis, como a detecção de situações de violência ou assédio moral.

## Citação

Se você utilizar o BeSIM em sua pesquisa, por favor, cite nosso artigo.

```bibtex
@inproceedings{falcao2024mllms,
  title={MLLMs e Interações Humanas: Construção e Avaliação de um Conjunto de Dados Brasileiro},
  author={Falcão, Mateus Souza and dos Santos, Vitória Sofia Vieira and Simões, Francisco Paulo Magalhaes},
  year={2024}
}
