# 6 总结与展望

## 6.1 结论

本文围绕"基于 Agent 的课程助教系统"的设计与实现进行了研究。在对大语言模型[3][5]、检索增强生成[7]、多智能体编排[8][9][13]等关键技术进行分析的基础上，完成了系统的需求分析、总体设计、详细设计与数据库设计，并基于 LangChain、LangGraph、FastAPI 等技术栈[13][14]实现了具有答疑、批改、出题三大核心功能并面向学生、教师、管理员三类用户的课程助教系统。

本文完成的主要工作包括：

（1）完成了系统需求分析。明确了系统面向学生、教师、管理员三类用户的核心功能需求与非功能需求，并从技术、经济、操作三方面论证了系统的可行性。

（2）完成了系统设计。设计了前后端分离的分层架构，将答疑、批改、出题三个智能体纳入基于 LangGraph 的编排工作流，实现了关键词路由与统一调度；设计了支撑答疑、批改、出题、学情统计等功能的数据模型与 16 张数据表。

（3）实现了系统核心功能。答疑 Agent 结合 FAISS 向量检索与大语言模型实现带溯源的流式多轮答疑，回答可标注"参考来源"；批改 Agent 以结构化 JSON 输出评分与评语；出题 Agent 依据知识点与难度批量生成试题；教师可上传文档构建知识库并查看学情看板。

（4）完成了系统测试。通过功能测试与自动化单元测试对各模块进行了验证，核心功能流程完整、正确，测试全部通过。

本系统的实现验证了基于 Agent 与检索增强生成的教学辅助系统在课程答疑、作业批改、试题生成等场景中的可用性，能够在一定程度上减轻人工助教负担、提升教学辅助效率。

## 6.2 展望

由于研究时间与个人能力有限，本系统仍存在一些不足，有待后续改进：

（1）答疑效果的深入优化。当前答疑主要依赖通用大语言模型与课程知识库，后续可通过参数调整时大模型微调（如 LoRA）等方式，使回答更贴合课程与教学风格。

（2）个性化学习支持。系统目前以答疑与批改为主，后续可结合学生的答题记录与学情数据，提供个性化的错题推荐与学习路径建议。

（3）工具调用能力的扩展。当前 Function Calling 已演示了工具调用闭环，后续可接入更多课程相关工具（如代码运行、图形绘制、在线评测等），进一步拓展答疑与出题能力。

（4）安全与审计完善。系统目前口令采用哈希简化存储、会话存储在内存中，后续可引入加盐加密、令牌有效期管理、Redis 会话持久化与更完善的审计日志，提升系统的安全性与健壮性。

（5）大规模并发与部署。系统后续可优化大模型调用的缓存与并发控制，采用容器化部署，以支撑更大规模的教学场景。

---

# 参考文献

[1] 何克抗. 信息技术与课程深层次整合的理论与方法[J]. 中国电化教育，2005（1）：17-29.

[2] 祝智庭，胡姣. 教育数字化转型的实践逻辑与发展机遇[J]. 电化教育研究，2022，43（1）：5-15.

[3] A. Vaswani, N. Shazeer, N. Parmar, et al. Attention Is All You Need[C]. Advances in Neural Information Processing Systems 30 (NeurIPS 2017), 2017: 5998-6008.

[4] J. Devlin, M.-W. Chang, K. Lee, et al. BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding[C]. Proceedings of the 2019 Conference of the NAACL: Human Language Technologies, Volume 1 (Long and Short Papers), 2019: 4171-4186.

[5] T. B. Brown, B. Mann, N. Ryder, et al. Language Models are Few-Shot Learners[C]. Advances in Neural Information Processing Systems 33 (NeurIPS 2020), 2020: 1877-1901.

[6] J. Wei, X. Wang, D. Schuurmans, et al. Chain-of-Thought Prompting Elicits Reasoning in Large Language Models[C]. Advances in Neural Information Processing Systems 35 (NeurIPS 2022), 2022: 24824-24837.

[7] P. Lewis, E. Perez, A. Piktus, et al. Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks[C]. Advances in Neural Information Processing Systems 33 (NeurIPS 2020), 2020: 9459-9474.

[8] S. Yao, J. Zhao, D. Yu, et al. ReAct: Synergizing Reasoning and Acting in Language Models[C]. International Conference on Learning Representations (ICLR), 2023.

[9] T. Schick, J. Dwivedi-Yu, R. Dessì, et al. Toolformer: Language Models Can Teach Themselves to Use Tools[C]. Advances in Neural Information Processing Systems 36 (NeurIPS 2023), 2023: 68539-68551.

[10] T. Kojima, S. Gu, M. Reid, et al. Large Language Models are Zero-Shot Reasoners[C]. Advances in Neural Information Processing Systems 35 (NeurIPS 2022), 2022: 22199-22213.

[11] J. S. Park, J. O'Brien, C. J. Cai, et al. Generative Agents: Interactive Simulacra of Human Behavior[C]. Proceedings of the 36th Annual ACM Symposium on User Interface Software and Technology (UIST), 2023: 1-22.

[12] J. Johnson, M. Douze, H. Jégou. Billion-Scale Similarity Search with GPUs[J]. IEEE Transactions on Big Data, 2021, 7（3）：535-547.

[13] LangChain AI. LangChain & LangGraph Documentation[EB/OL]. https://python.langchain.com/.

[14] FastAPI. FastAPI: Modern, fast, (high-performance) web framework for building APIs[EB/OL]. https://fastapi.tiangolo.com/.

[15] Facebook Research. FAISS: A Library for Efficient Similarity Search and Clustering of Dense Vectors[EB/OL]. https://github.com/facebookresearch/faiss.

[16] 张华，等. 生成式人工智能背景下高校智能教学系统的设计与应用[J]. 现代教育技术，2024（10）：56-64.

---

# 附  录A（如有）

系统部署说明与演示数据见项目 README 与初始化脚本。

---

# 致  谢

在毕业设计完成之际，由衷感谢所有给予我帮助与支持的人。

首先，特别感谢我的指导老师***。从课题选题、方案设计到系统开发与论文撰写，老师都给予了悉心的指导和中肯的建议。在我遇到技术难题时，老师耐心地引导我分析问题、寻找解决办法，帮助我逐步完成了系统的设计与实现。

感谢学院以及人工智能与大数据学院各位老师四年来的教导与培养，使我打下了扎实的专业基础。感谢同学们在学习和生活中的帮助与鼓励，与你们一起学习和讨论让我受益匪浅。

最后，感谢家人在我求学期间一如既往的支持与理解，你们的陪伴是我不断前行的动力。

由于水平和时间有限，本论文难免存在疏漏之处，恳请各位老师和专家批评指正。