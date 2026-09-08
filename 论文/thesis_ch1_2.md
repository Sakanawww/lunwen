# 基于 Agent 的课程助教系统设计与实现

（本文件为论文正文草稿。占位符如「【图3.1】」「【表4.1】」「【截图：…】」表示需在该位置插入对应图表或截图，待样板后统一制作。）

---

## 摘  要

随着人工智能技术的快速发展，大语言模型（Large Language Model, LLM）在自然语言处理领域取得了显著进展，并在教育领域展现出广阔的应用前景。传统高校课程助教虽能完成答疑、作业批改与出题等工作，但普遍存在响应不及时、批改标准不统一、依赖人工重复劳动等问题，难以满足大规模个性化教学的需求。

针对上述问题，本文设计并实现了一个基于 Agent 架构的课程助教系统。系统以 LangChain 与 LangGraph 为核心框架，构建了答疑、批改、出题三个相互协作的智能体（Agent）：答疑 Agent 结合检索增强生成（Retrieval-Augmented Generation, RAG）技术，基于课程知识库进行流式回答并附带溯源引用；批改 Agent 依据预设评分标准对学生作业进行智能评分并生成评语；出题 Agent 依据知识点与难度批量生成试题。系统采用前后端分离的服务架构，后端基于 FastAPI 构建 Web 服务，接入云端大模型 API，前端基于 Jinja2 模板实现学生、教师、管理员三端页面，实现流式对话、知识库管理、作业批改、试题管理与学情看板等核心功能。系统通过漏斗式关键词路由实现多 Agent 协作调度，并利用 Function Calling 机制完成函数调用闭环。

本文详细阐述了系统的需求分析、总体设计、详细设计、数据库设计及系统实现，并通过功能测试验证了各模块的可用性与正确性。测试结果表明，系统能够有效支持课程教学中答疑、批改与出题等核心环节，提升了教学辅助工作的效率与质量，具有良好的可用性与扩展性。

**关键词**：大语言模型；检索增强生成；多智能体；答疑系统；课程助教

---

## Abstract

With the rapid development of artificial intelligence, large language models (LLMs) have made significant progress in the field of natural language processing and shown broad application prospects in education. Traditional university course teaching assistants can complete tasks such as answering questions, grading assignments, and generating exercises, but generally suffer from problems such as untimely responses, inconsistent grading standards, and heavy reliance on repetitive manual labor, which makes it difficult to meet the needs of large-scale personalized teaching.

To address these problems, this thesis designs and implements a course teaching assistant system based on the Agent architecture. Using LangChain and LangGraph as the core frameworks, the system builds three collaborating agents, namely the Q&A agent, the grading agent, and the question-generation agent. The Q&A agent combines Retrieval-Augmented Generation (RAG) technology to provide streaming answers based on the course knowledge base with source tracing. The grading agent scores student assignments according to preset criteria and generates feedback. The question-generation agent generates exercises in batches according to knowledge points and difficulty. The system adopts a front-end and back-end separated service architecture. The back end is built with FastAPI and connects to cloud-based LLM APIs, while the front end uses Jinja2 templates to implement student, teacher, and administrator pages for core functions such as streaming dialogue, knowledge base management, assignment grading, exercise management, and a learning analytics dashboard. The system implements multi-agent collaborative scheduling through keyword-based routing and completes the function-calling loop through the Function Calling mechanism.

This thesis elaborates on the system's requirements analysis, overall design, detailed design, database design, and system implementation, and verifies the usability and correctness of each module through functional testing. The test results show that the system can effectively support the core links of Q&A, grading, and question generation in course teaching, improve the efficiency and quality of teaching assistance, and has good usability and scalability.

**Key words**: Large Language Model; Retrieval-Augmented Generation; Multi-Agent; Q&A System; Course Teaching Assistant

---

# 1 绪论

## 1.1 研究背景及意义

人工智能（Artificial Intelligence, AI）技术的飞速发展正在深刻改变各行业的运作方式，教育领域亦是如此。近年来，以深度学习为代表的人工智能技术在教育中的应用日益广泛，从智能阅卷、个性化推荐到自适应学习，智能教育已经成为高校信息化建设的重要方向[1][2]。2022 年底以来，以大语言模型为代表的新一代生成式人工智能（Generative AI）技术迅速崛起，极大地拓展了机器在文本理解、生成、推理等方面的能力边界，为构建更智能、更人性化的教育教学辅助工具提供了新的可能[3][5]。

在高校课程教学过程中，助教承担着答疑、批改作业、出题等大量基础性教学辅助工作。然而，传统的人工助教模式面临诸多现实问题：一方面，随着课程选课人数增多，学生提问数量大幅上升，人工助教难以随时响应，易出现回答不及时或遗漏；另一方面，不同助教对主观题作业的评分标准理解不一，批改结果的一致性难以保证；此外，出题与组卷需要耗费大量精力和专业积累，重复性强且效率不高。这些问题制约了教学辅助工作的效率与质量。

在计算机科学与技术专业课程（如《数据结构》）的教学实践中，上述矛盾尤为突出。该课程概念抽象、算法较多，学生课后疑问集中，作业批改工作量大。因此，研究并实现一个基于智能体的课程助教系统，利用大语言模型的能力自动完成答疑、批改与出题任务，具有重要的现实意义：

（1）提高答疑效率。通过检索增强生成技术，系统能够基于课程知识库快速、准确地回答学生的课程相关问题，并结合来源引用增强回答的可信度，缓解人工助教响应不及时的问题。

（2）提升批改一致性。系统按照统一的评分标准对学生作业进行智能批改，并输出针对性的评语与改进建议，有助于提高作业批改的客观性与一致性。

（3）减轻重复劳动。系统能够依据知识点与难度要求自动生成试题，帮助教师快速组卷，减少机械性、重复性的出题工作。

（4）促进教学数据积累。系统记录学生的答疑、批改与答题记录，并通过学情看板进行统计分析，为教师了解学情、改进教学提供数据支持。

## 1.2 国内外研究现状

### 1.2.1 国内研究现状

国内在人工智能与教育融合领域的研究起步较早，成果丰富。早期研究集中于智能答疑系统、知识库问答平台等方向，主要采用基于规则匹配、检索式问答或知识图谱等技术构建辅助教学工具，这类系统在特定知识范围内表现良好，但受限于知识表示与自然语言理解能力，难以处理开放式、发散性的提问[1][2]。

近年来，随着大语言模型在国内的落地应用，越来越多的研究开始关注生成式人工智能在教学中的应用价值[16]。国内学者围绕大模型在智能教学、个性化学习、作业批改等场景进行了广泛探讨，普遍认为大语言模型有望在教学辅助、学业诊断、内容生成等方面发挥重要作用。同时，RAG 检索增强生成技术通过将外部知识源引入模型生成过程，有效缓解了大模型在专业、领域性知识上的不足与幻觉问题，成为构建领域智能化应用的重要技术路线[7]。

### 1.2.2 国外研究现状

国外在智能教学系统（Intelligent Tutoring System, ITS）与教育技术领域有着深厚的研究积累。早期智能教学系统强调对学生知识状态建模与个性化反馈，但对自然语言交互的支持较为有限。随着深度学习与 Transformer 架构的提出[3][4]，预训练语言模型在文本生成与理解上的能力大幅提升，为构建对话式教学系统奠定了基础[5][6]。

2020 年前后，外部检索与大模型结合的思想逐渐成熟，RAG 技术通过对大规模语料库进行检索并在生成阶段利用检索结果，显著提高了问答等知识密集型任务的准确性与可控性[7]。近年来，面向工具使用的 Agent 框架与函数调用机制使大语言模型能够调用外部工具完成多步骤任务[8][9]，多智能体协作以及像 LangChain、LangGraph 这样的编排框架进一步推动了复杂智能应用的研究[11][13]。这些工作为本系统的设计提供了重要的技术参考。

## 1.3 研究内容和方法

### 1.3.1 研究内容

本文围绕"基于 Agent 的课程助教系统"的设计与实现展开研究，主要研究内容包括以下几个方面：

第一部分为绪论。阐述课题研究的背景和意义，综述国内外相关研究现状，说明本文的研究内容与方法。

第二部分为系统关键技术介绍。对系统实现所依赖的核心技术进行说明，包括大语言模型与提示工程、检索增强生成（RAG）、LangChain 与 LangGraph 多智能体编排框架、FAISS 向量检索、Function Calling 函数调用机制以及 FastAPI 与服务器推送（SSE）技术等。

第三部分为系统需求分析。分析系统的总体需求，围绕学生、教师、管理员三类角色开展功能需求分析与非功能需求分析，并从技术可行性与经济可行性两方面进行分析。

第四部分为系统设计。阐述系统的总体设计与详细设计，说明三端页面与三大智能体的模块划分，设计数据结构，给出系统 E-R 图与数据库表结构。

第五部分为系统实现。介绍系统的开发与运行环境，对各功能模块的实现进行说明，并结合页面与核心代码逻辑展示答疑流式问答、AI 批改、智能出题、知识库管理、学情看板等功能的实现过程，最后阐述系统的测试方法与测试结果。

第六部分为总结与展望。总结本文的主要工作与成果，分析系统存在的不足，并对后续改进方向进行展望。

### 1.3.2 研究方法

（1）文献研究法。通过查阅国内外关于大语言模型、检索增强生成、多智能体系统、智能教学系统等方面的文献资料，梳理相关理论与技术现状，为系统设计提供理论依据。

（2）软件工程方法。按照软件工程的需求分析、概要设计、详细设计、编码实现、系统测试等流程，规范地组织系统的开发过程，保证系统的完整性与可用性。

（3）实验验证法。在真实环境下搭建系统运行环境，接入云端大语言模型 API，对系统各功能模块进行运行测试，验证系统功能的正确性与可用性。