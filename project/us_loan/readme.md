需要将 SEC 8-K 申报文件中的非结构化文本（贷款合同）转换为结构化数据（您图片中的表格）。

这是一个典型的“文档布局分析”和“自然语言处理 (NLP)”相结合的任务。根据您的文件结构和需求，我为您规划了以下执行路径。

我们将优先处理 `...123.txt` 这种“完全提交文本文件”（Complete Submission Text File），因为它们通常在一个文件中包含了元数据和所有附件，便于程序化处理。

------



### 🚀 项目执行蓝图





#### 步骤一：遍历文件系统



首先，我们需要遍历您下载的 `sec_data` 目录，找到每一个独立的申报文件（filing）。

- 使用 Python 的 `os.walk`。
- 目标是定位到每个 `[Filing_ID]` 文件夹（如 `000032019324000123`）。
- 在这个文件夹中，我们的关键目标是那个 **`...123.txt`** 文件。它包含了该次申报的所有信息。
- 同时，从路径中提取 `CIK`（公司ID，如 `320193`）和 `Accession Number`（申报ID，即 `Filing_ID`，如 `000032019324000123`）。



#### 步骤二：解析主申报文件 (....123.txt) 并提取元数据



这个 `.txt` 文件是SEC的标准格式。它由一个头部 `<SEC-HEADER>` 和一个或多个 `<DOCUMENT>` 块组成。

1. **读取主 `.txt` 文件**：将整个文件读入内存。
2. **提取元数据**：使用正则表达式 (RegEx) 从 `<SEC-HEADER>` 块中提取：
   - **公司名称**: 匹配 `COMPANY CONFORMED NAME: (.*?)\n`
   - **贷款起效日期**: 匹配 `FILING DATE: (\d{8})\n` (这将得到 YYYYMMDD 格式，如 `20240930`)。
   - **公司 ID (CIK)**: `CENTRAL INDEX KEY: (.*?)\n` (用于验证)
3. **贷款合同 ID**: 我们使用 `Accession Number` (即 `Filing_ID`) 作为唯一的合同（申报）ID，这符合您表格中“同一合同ID下有多句”的逻辑。



#### 步骤三：定位并分离 "Credit Agreement" 附件



主 `.txt` 文件将其所有附件（Exhibits）都包含在 `<DOCUMENT>...</DOCUMENT>` 标签对中。

1. **分割文档**: 使用 `file_content.split('<DOCUMENT>')` 将文件分割成多个部分。
2. **遍历附件**: 循环遍历每个分割后的“文档块”。
3. **识别附件类型**: 在每个块的开头，查找 `<TYPE>` 标签。我们重点关注 `EX-10` 系列 (如 `EX-10.1`, `EX-10.2`...)，因为这些是“重大合同”。
4. **识别“贷款合同”**: 在找到 `EX-10` 类型的附件后，检查其描述文本（在 `<TYPE>` 标签附近，但在 `<TEXT>` 标签之前）是否包含关键词 **"Credit Agreement"** （不区分大小写）。



#### 步骤四：解析合同文本并提取句子 (NLP 核心)



一旦确认某个 `<DOCUMENT>` 块是我们要找的 "Credit Agreement"：

1. **提取纯文本**:
   - 定位到该块中的 `<TEXT>...</TEXT>` 标签。
   - 内部通常是 HTML。使用 `BeautifulSoup` 库来解析并提取所有纯文本。
   - `BeautifulSoup(html_content, 'html.parser').get_text()`
2. **句子分割 (Sentence Tokenization)**:
   - 将获取到的整篇纯文本分割成独立的句子。**强烈建议**使用 `nltk` 库的 `sent_tokenize`，而不是简单地按 `.` 分割（因为它能正确处理 "Mr."、"U.S." 等情况）。
   - `import nltk; nltk.download('punkt'); sentences = nltk.sent_tokenize(clean_text)`
3. **关键词匹配**:
   - 定义您的关键词列表: `keywords = ['supplier', 'customer', 'supply chain', 'supply-chain']`
   - 遍历所有句子，将句子转为小写 (`sentence.lower()`)，然后检查是否**至少包含**列表中的一个关键词。
   - `if any(k in sentence.lower() for k in keywords):`
4. **收集结果**: 如果一个句子匹配成功，就将其（**原始大小写的句子**）与步骤二中提取的元数据（CIK, 公司名称, Filing_ID, 日期）组合在一起。



#### 步骤五：构建并输出表格



1. **汇总数据**: 将所有匹配到的数据行（每行包含 CIK、公司名、合同ID、日期、句子）添加到一个 Python 列表中。

2. 创建 DataFrame: 使用 pandas 库将这个列表转换为 DataFrame。

   df = pd.DataFrame(all_results, columns=['公司 ID', '公司名称', '贷款合同 ID', '贷款起效日期', '含供应链信息句子'])

3. **保存文件**: `df.to_csv('supply_chain_sentences.csv', index=False, encoding='utf-8-sig')`

------



### 🐍 关键技术和 Python 库



- `os`: 遍历文件目录 (`os.walk`)。
- `re` (RegEx): 用于从 `<SEC-HEADER>` 和附件描述中提取信息。
- `bs4` (BeautifulSoup): 用于解析附件中的 HTML，提取纯文本。
- `nltk` (Natural Language Toolkit): 用于准确地将合同文本分割成句子 (`sent_tokenize`)。
- `pandas`: 用于组织最终数据并导出为 CSV/Excel。

------



### 💡 重要提示和替代方案



- **处理 `.htm` 文件（您的备用路径）**:
  - 您提供的目录结构中也包含独立的 `.htm` 文件 (如 `0001-aapl-20240930.htm`)。如果 `.txt` 文件不存在或处理困难，您可以改变策略：
  - 1. 解析**主 `.htm` 文件** (`...aapl-20240930.htm`)。
  - 1. 在其中找到 "Exhibit Index"（通常是一个HTML表格）。
  - 1. 查找描述为 "Credit Agreement" 的行，并获取其对应的链接（`<a>` 标签的 `href`），这通常指向一个附件文件（如 `0002-(ex...).htm`）。
  - 1. 打开并解析这个**附件 `.htm` 文件**，然后执行上述的**步骤四**（NLP提取）。
  - *（但我仍然推荐优先处理 `.txt` 文件，因为它更统一。）*
- **性能**: 这个过程（特别是 NLP 部分）可能需要一些时间。建议先用一小部分 CIK（例如10个公司）进行测试。
- **关键词的局限性**: `customer` 和 `supplier` 可能会匹配到很多“噪音”（不相关的句子）。您可能需要后续人工审核，或者使用更复杂的 NLP 模型（如命名实体识别 "NER" 或关系提取）来提高准确率，但您当前的关键词策略是最好的起点。
