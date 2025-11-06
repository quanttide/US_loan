import os
import re
import logging
import pandas as pd
import nltk
from bs4 import BeautifulSoup
from tqdm import tqdm

# --- 配置与日志设置 ---
# (您的配置保持不变)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

config = {
    "root_dir": 'data/Archives/edgar/data/',
    "output_csv": 'extracted_supply_chain_sentences.csv',
    # 贷款合同相关关键词（英文SEC文档常用表述）
    "loan_keywords": [
        "credit agreement", "loan agreement", "financing agreement",
        "credit facility", "loan contract", "funding agreement"
    ],
    # 供应链相关关键词（英文）
    "supply_chain_keywords": [
        "supplier", "suppliers", "customer", "customers",
        "supply chain", "supply-chain", "procurement",
        "distribution", "upstream", "downstream"
    ]
}

# --- 预编译正则表达式（您的定义保持不变） ---
company_name_re = re.compile(r"COMPANY CONFORMED NAME:\s*(.*)", re.IGNORECASE)
filing_date_re = re.compile(r"FILING DATE:\s*(\d{8})", re.IGNORECASE)
effective_date_re = re.compile(
    r"(effective date|commencement date|start date)\s*[:;]?\s*(\d{2}/\d{2}/\d{4}|\d{4}-\d{2}-\d{2}|\d{8})",
    re.IGNORECASE
)
contract_id_re = re.compile(
    r"(contract number|agreement number|loan id)\s*[:;#]?\s*([A-Z0-9\-]+)",
    re.IGNORECASE
)


# --- NLTK 资源管理（您的函数保持不变） ---
def download_nltk_resource(resource_name):
    """检查并下载NLTK所需资源"""
    try:
        nltk.data.find(resource_name)
    except LookupError:
        short_name = resource_name.split('/')[-1]
        logging.info(f"Downloading NLTK resource: {short_name}")
        nltk.download(short_name, quiet=True)


logging.info("Checking NLTK resources...")
download_nltk_resource('tokenizers/punkt')
download_nltk_resource('tokenizers/punkt_tab')
logging.info("NLTK resources ready")


# --- 工具函数（您的函数保持不变） ---
def format_date(date_str):
    if not date_str: return "Unknown"
    if re.match(r"\d{8}", date_str):
        return f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:]}"
    if re.match(r"\d{2}/\d{2}/\d{4}", date_str):
        month, day, year = date_str.split('/')
        return f"{year}-{month}-{day}"
    if re.match(r"\d{4}-\d{2}-\d{2}", date_str):
        return date_str
    return date_str


def extract_clean_text_from_exhibit(file_content):
    try:
        text_match = re.search(r"<TEXT>(.*)</TEXT>", file_content, re.DOTALL | re.IGNORECASE)
        if text_match:
            html_content = text_match.group(1)
        else:
            html_content = file_content
        soup = BeautifulSoup(html_content, 'html.parser')
        for tag in soup(["table", "style", "script", "xref", "form"]):
            tag.decompose()
        text = soup.get_text(separator=' ')
        text = re.sub(r'\s+', ' ', text).strip()
        text = re.sub(r'[\x00-\x1F\x7F]', '', text)
        return text
    except Exception as e:
        logging.warning(f"Text extraction failed: {str(e)}")
        return ""


def get_metadata_from_main_file(filing_path, filing_id):
    target_file_nodash = os.path.join(filing_path, f"{filing_id}.txt")
    target_file_dash = ""
    if len(filing_id) == 18:
        dashed_name = f"{filing_id[0:10]}-{filing_id[10:12]}-{filing_id[12:18]}"
        target_file_dash = os.path.join(filing_path, f"{dashed_name}.txt")
    main_file_path = None
    if os.path.isfile(target_file_dash):
        main_file_path = target_file_dash
    elif os.path.isfile(target_file_nodash):
        main_file_path = target_file_nodash
    else:
        logging.warning(f"No main file found for filing {filing_id}")
        return "Unknown", "Unknown"
    try:
        with open(main_file_path, 'r', encoding='utf-8', errors='ignore') as f:
            header_content = f.read(5000)
        company_name_match = company_name_re.search(header_content)
        company_name = company_name_match.group(1).strip() if company_name_match else "Unknown"
        filing_date_match = filing_date_re.search(header_content)
        filing_date_raw = filing_date_match.group(1).strip() if filing_date_match else "Unknown"
        filing_date = format_date(filing_date_raw)
        return company_name, filing_date
    except Exception as e:
        logging.warning(f"Metadata extraction failed for {filing_id}: {str(e)}")
        return "Unknown", "Unknown"


#
# -----------------------------------------------------------------
# vvvvvv   已修改的函数 (Updated Function)   vvvvvv
# -----------------------------------------------------------------
#
def process_exhibit_file(exhibit_path, cik, filing_id, company_name, filing_date):
    """处理单个附件文件，提取贷款合同中的供应链相关信息"""
    results = []
    try:
        # 步骤 1: 读取文件内容
        with open(exhibit_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        # 步骤 2:【关键优化】
        # 首先对 *原始文本* 头部进行快速检查。
        # 这会捕获 <DESCRIPTION> 标签和文件标题，且成本极低。
        # 我们检查前 5000 个字符。
        content_head_lower = content[:5000].lower()
        if not any(kw in content_head_lower for kw in config["loan_keywords"]):
            return []  # 快速拒绝不相关的附件

        # 步骤 3: 提取纯文本（现在只对“疑似”合同的文件执行此操作）
        clean_text = extract_clean_text_from_exhibit(content)
        if not clean_text:
            return []

        # 步骤 4: 提取合同生效日期（您的逻辑）
        effective_date = filing_date  # 默认为文件提交日期
        effective_date_match = effective_date_re.search(clean_text)
        if effective_date_match:
            effective_date = format_date(effective_date_match.group(2))

        # 步骤 5: 提取合同编号（您的逻辑）
        contract_id = filing_id  # 默认为申报ID
        contract_id_match = contract_id_re.search(clean_text)
        if contract_id_match:
            contract_id = contract_id_match.group(2).strip()

        # 步骤 6: 分割句子（您的逻辑）
        try:
            sentences = nltk.sent_tokenize(clean_text)
        except Exception as e:
            logging.warning(f"NLTK tokenization failed for {exhibit_path}: {str(e)}")
            sentences = re.split(r'[.!?;]\s+', clean_text)

        # 步骤 7: 筛选含供应链关键词的句子
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 30:  # 您的过滤器
                continue

            if any(kw in sentence.lower() for kw in config["supply_chain_keywords"]):
                results.append({
                    "公司 ID": cik,
                    "公司名称": company_name,
                    "贷款合同 ID": contract_id,
                    "贷款起效日期": effective_date,
                    "含供应链信息句子": sentence
                })

    except Exception as e:
        logging.error(f"Error processing exhibit {exhibit_path}: {str(e)}")

    return results


# -----------------------------------------------------------------
# ^^^^^^   已修改的函数 (Updated Function)   ^^^^^^
# -----------------------------------------------------------------
#

# --- Main 函数（您的函数保持不变） ---
def main():
    logging.info(f"Starting processing from directory: {config['root_dir']}")

    all_results = []
    filing_dirs_to_process = []

    for cik_dir in os.listdir(config["root_dir"]):
        cik_path = os.path.join(config["root_dir"], cik_dir)
        if not os.path.isdir(cik_path):
            continue

        for filing_dir in os.listdir(cik_path):
            filing_path = os.path.join(cik_path, filing_dir)
            if os.path.isdir(filing_path):
                filing_dirs_to_process.append((cik_dir, filing_dir, filing_path))

    logging.info(f"Found {len(filing_dirs_to_process)} filing directories to process")

    for cik, filing_id, filing_path in tqdm(filing_dirs_to_process, desc="Processing filings"):
        company_name, filing_date = get_metadata_from_main_file(filing_path, filing_id)

        try:
            for filename in os.listdir(filing_path):
                fn_upper = filename.upper()
                is_exhibit = "(EX-" in fn_upper or "_EX" in fn_upper
                is_text_file = fn_upper.endswith((".HTM", ".HTML", ".TXT"))

                if is_exhibit and is_text_file:
                    exhibit_path = os.path.join(filing_path, filename)
                    all_results.extend(
                        process_exhibit_file(exhibit_path, cik, filing_id, company_name, filing_date)
                    )
        except Exception as e:
            logging.error(f"Error scanning directory {filing_path}: {str(e)}")

    if not all_results:
        logging.info("Processing complete. No matching data found.")
        return

    logging.info(f"Processing complete. Found {len(all_results)} matching sentences.")

    df = pd.DataFrame(all_results)
    df = df[["公司 ID", "公司名称", "贷款合同 ID", "贷款起效日期", "含供应链信息句子"]]
    df = df.drop_duplicates()

    try:
        df.to_csv(config["output_csv"], index=False, encoding='utf-8-sig')
        logging.info(f"Results saved to: {config['output_csv']}")
    except Exception as e:
        logging.error(f"Failed to save CSV: {str(e)}")


if __name__ == "__main__":
    main()