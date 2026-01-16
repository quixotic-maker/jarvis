"""
文档加载器
支持多种文件格式的加载和解析
"""
from typing import Optional, Dict, Any, List
from pathlib import Path
import logging
import chardet
from datetime import datetime
import mimetypes

logger = logging.getLogger(__name__)


class DocumentLoader:
    """文档加载器基类"""
    
    def __init__(self):
        """初始化加载器"""
        self.supported_extensions: List[str] = []
    
    def can_load(self, file_path: str) -> bool:
        """
        检查是否支持加载该文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            bool: 是否支持
        """
        ext = Path(file_path).suffix.lower()
        return ext in self.supported_extensions
    
    def load(self, file_path: str) -> Dict[str, Any]:
        """
        加载文档
        
        Args:
            file_path: 文件路径
            
        Returns:
            Dict: 包含content和metadata的字典
        """
        raise NotImplementedError("子类必须实现load方法")
    
    def extract_metadata(self, file_path: str) -> Dict[str, Any]:
        """
        提取文件元数据
        
        Args:
            file_path: 文件路径
            
        Returns:
            Dict: 元数据字典
        """
        path = Path(file_path)
        
        metadata = {
            "file_name": path.name,
            "file_path": str(path.absolute()),
            "file_extension": path.suffix.lower(),
            "file_size": path.stat().st_size if path.exists() else 0,
        }
        
        if path.exists():
            stat = path.stat()
            metadata.update({
                "created_time": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "modified_time": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            })
        
        # MIME类型
        mime_type, _ = mimetypes.guess_type(str(path))
        if mime_type:
            metadata["mime_type"] = mime_type
        
        return metadata


class TextLoader(DocumentLoader):
    """纯文本加载器"""
    
    def __init__(self):
        super().__init__()
        self.supported_extensions = ['.txt', '.text', '.log']
    
    def load(self, file_path: str) -> Dict[str, Any]:
        """
        加载文本文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            Dict: 文档内容和元数据
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        # 检测编码
        with open(path, 'rb') as f:
            raw_data = f.read()
            result = chardet.detect(raw_data)
            encoding = result['encoding'] or 'utf-8'
        
        # 读取文本
        try:
            with open(path, 'r', encoding=encoding) as f:
                content = f.read()
        except UnicodeDecodeError:
            # 如果解码失败，尝试utf-8
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            encoding = 'utf-8 (with errors ignored)'
        
        # 提取元数据
        metadata = self.extract_metadata(file_path)
        metadata.update({
            "encoding": encoding,
            "line_count": content.count('\n') + 1,
            "character_count": len(content),
            "loader_type": "TextLoader"
        })
        
        logger.info(f"文本文件加载成功: {path.name} ({len(content)} 字符)")
        
        return {
            "content": content,
            "metadata": metadata
        }


class MarkdownLoader(DocumentLoader):
    """Markdown文档加载器"""
    
    def __init__(self):
        super().__init__()
        self.supported_extensions = ['.md', '.markdown', '.mdown']
    
    def load(self, file_path: str) -> Dict[str, Any]:
        """
        加载Markdown文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            Dict: 文档内容和元数据
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        # 读取文件（类似TextLoader）
        with open(path, 'rb') as f:
            raw_data = f.read()
            result = chardet.detect(raw_data)
            encoding = result['encoding'] or 'utf-8'
        
        try:
            with open(path, 'r', encoding=encoding) as f:
                content = f.read()
        except UnicodeDecodeError:
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            encoding = 'utf-8 (with errors ignored)'
        
        # 提取Markdown特有的元数据
        metadata = self.extract_metadata(file_path)
        markdown_meta = self._parse_markdown_metadata(content)
        
        metadata.update({
            "encoding": encoding,
            "line_count": content.count('\n') + 1,
            "character_count": len(content),
            "loader_type": "MarkdownLoader",
            **markdown_meta
        })
        
        logger.info(f"Markdown文件加载成功: {path.name}")
        
        return {
            "content": content,
            "metadata": metadata
        }
    
    def _parse_markdown_metadata(self, content: str) -> Dict[str, Any]:
        """
        解析Markdown文档的结构信息
        
        Args:
            content: Markdown内容
            
        Returns:
            Dict: 元数据
        """
        import re
        
        meta = {}
        
        # 统计标题数量
        headers = re.findall(r'^#+\s+.+$', content, re.MULTILINE)
        meta["header_count"] = len(headers)
        
        # 提取第一个标题作为标题
        if headers:
            first_header = headers[0].lstrip('#').strip()
            meta["title"] = first_header
        
        # 统计代码块数量
        code_blocks = re.findall(r'```[\s\S]*?```', content)
        meta["code_block_count"] = len(code_blocks)
        
        # 统计链接数量
        links = re.findall(r'\[([^\]]+)\]\(([^\)]+)\)', content)
        meta["link_count"] = len(links)
        
        # 统计图片数量
        images = re.findall(r'!\[([^\]]*)\]\(([^\)]+)\)', content)
        meta["image_count"] = len(images)
        
        return meta


class CodeLoader(DocumentLoader):
    """代码文件加载器"""
    
    def __init__(self):
        super().__init__()
        self.supported_extensions = [
            '.py', '.js', '.ts', '.jsx', '.tsx',
            '.java', '.cpp', '.c', '.h', '.hpp',
            '.go', '.rs', '.rb', '.php',
            '.html', '.css', '.scss', '.sass',
            '.json', '.xml', '.yaml', '.yml'
        ]
        
        # 语言映射
        self.language_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.jsx': 'javascript-react',
            '.tsx': 'typescript-react',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'c',
            '.go': 'go',
            '.rs': 'rust',
            '.rb': 'ruby',
            '.php': 'php',
            '.html': 'html',
            '.css': 'css',
            '.json': 'json',
            '.xml': 'xml',
            '.yaml': 'yaml',
            '.yml': 'yaml'
        }
    
    def load(self, file_path: str) -> Dict[str, Any]:
        """
        加载代码文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            Dict: 代码内容和元数据
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        # 读取文件
        with open(path, 'rb') as f:
            raw_data = f.read()
            result = chardet.detect(raw_data)
            encoding = result['encoding'] or 'utf-8'
        
        try:
            with open(path, 'r', encoding=encoding) as f:
                content = f.read()
        except UnicodeDecodeError:
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            encoding = 'utf-8 (with errors ignored)'
        
        # 提取代码元数据
        metadata = self.extract_metadata(file_path)
        code_meta = self._analyze_code(content, path.suffix.lower())
        
        metadata.update({
            "encoding": encoding,
            "language": self.language_map.get(path.suffix.lower(), 'unknown'),
            "loader_type": "CodeLoader",
            **code_meta
        })
        
        logger.info(f"代码文件加载成功: {path.name} ({metadata['language']})")
        
        return {
            "content": content,
            "metadata": metadata
        }
    
    def _analyze_code(self, content: str, extension: str) -> Dict[str, Any]:
        """
        分析代码结构
        
        Args:
            content: 代码内容
            extension: 文件扩展名
            
        Returns:
            Dict: 代码元数据
        """
        import re
        
        meta = {
            "line_count": content.count('\n') + 1,
            "character_count": len(content),
        }
        
        # Python代码分析
        if extension == '.py':
            classes = re.findall(r'^\s*class\s+(\w+)', content, re.MULTILINE)
            functions = re.findall(r'^\s*def\s+(\w+)', content, re.MULTILINE)
            imports = re.findall(r'^\s*(?:from\s+\S+\s+)?import\s+.+$', content, re.MULTILINE)
            
            meta.update({
                "class_count": len(classes),
                "function_count": len(functions),
                "import_count": len(imports),
                "classes": classes[:10],  # 最多10个
                "functions": functions[:10]
            })
        
        # JavaScript/TypeScript分析
        elif extension in ['.js', '.ts', '.jsx', '.tsx']:
            classes = re.findall(r'class\s+(\w+)', content)
            functions = re.findall(r'function\s+(\w+)|const\s+(\w+)\s*=.*?=>', content)
            imports = re.findall(r'import\s+.+\s+from\s+["\'].+["\']', content)
            
            # 展平函数名列表
            func_names = [f[0] or f[1] for f in functions if f[0] or f[1]]
            
            meta.update({
                "class_count": len(classes),
                "function_count": len(func_names),
                "import_count": len(imports)
            })
        
        # 统计注释（通用）
        single_line_comments = len(re.findall(r'//.*$|#.*$', content, re.MULTILINE))
        multi_line_comments = len(re.findall(r'/\*[\s\S]*?\*/|"""[\s\S]*?"""|\'\'\'[\s\S]*?\'\'\'', content))
        meta["comment_count"] = single_line_comments + multi_line_comments
        
        # 计算代码密度（非空行 / 总行数）
        non_empty_lines = len([line for line in content.split('\n') if line.strip()])
        total_lines = meta["line_count"]
        meta["code_density"] = round(non_empty_lines / total_lines, 2) if total_lines > 0 else 0
        
        return meta


class PDFLoader(DocumentLoader):
    """PDF文档加载器"""
    
    def __init__(self):
        super().__init__()
        self.supported_extensions = ['.pdf']
    
    def load(self, file_path: str) -> Dict[str, Any]:
        """
        加载PDF文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            Dict: PDF内容和元数据
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        try:
            import PyPDF2
        except ImportError:
            logger.error("PyPDF2未安装，无法加载PDF文件")
            raise ImportError("请安装PyPDF2: pip install PyPDF2")
        
        # 读取PDF
        content_parts = []
        with open(path, 'rb') as f:
            pdf_reader = PyPDF2.PdfReader(f)
            page_count = len(pdf_reader.pages)
            
            for page_num, page in enumerate(pdf_reader.pages):
                try:
                    text = page.extract_text()
                    if text:
                        content_parts.append(text)
                except Exception as e:
                    logger.warning(f"PDF页面 {page_num + 1} 提取失败: {e}")
        
        content = '\n\n'.join(content_parts)
        
        # 提取元数据
        metadata = self.extract_metadata(file_path)
        metadata.update({
            "page_count": page_count,
            "character_count": len(content),
            "loader_type": "PDFLoader"
        })
        
        # 尝试获取PDF元数据
        try:
            with open(path, 'rb') as f:
                pdf_reader = PyPDF2.PdfReader(f)
                if pdf_reader.metadata:
                    pdf_meta = pdf_reader.metadata
                    if pdf_meta.get('/Title'):
                        metadata["title"] = pdf_meta.get('/Title')
                    if pdf_meta.get('/Author'):
                        metadata["author"] = pdf_meta.get('/Author')
                    if pdf_meta.get('/Subject'):
                        metadata["subject"] = pdf_meta.get('/Subject')
        except Exception as e:
            logger.warning(f"PDF元数据提取失败: {e}")
        
        logger.info(f"PDF文件加载成功: {path.name} ({page_count} 页)")
        
        return {
            "content": content,
            "metadata": metadata
        }


class LoaderFactory:
    """加载器工厂"""
    
    def __init__(self):
        """初始化工厂"""
        self.loaders = [
            TextLoader(),
            MarkdownLoader(),
            CodeLoader(),
            PDFLoader()
        ]
    
    def get_loader(self, file_path: str) -> Optional[DocumentLoader]:
        """
        根据文件路径获取合适的加载器
        
        Args:
            file_path: 文件路径
            
        Returns:
            Optional[DocumentLoader]: 加载器实例，如果不支持则返回None
        """
        for loader in self.loaders:
            if loader.can_load(file_path):
                return loader
        
        logger.warning(f"不支持的文件类型: {file_path}")
        return None
    
    def load_document(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        加载文档（自动选择加载器）
        
        Args:
            file_path: 文件路径
            
        Returns:
            Optional[Dict]: 文档内容和元数据，如果加载失败返回None
        """
        loader = self.get_loader(file_path)
        if loader is None:
            return None
        
        try:
            return loader.load(file_path)
        except Exception as e:
            logger.error(f"文档加载失败 {file_path}: {e}")
            return None


# 单例实例
_loader_factory: Optional[LoaderFactory] = None


def get_loader_factory() -> LoaderFactory:
    """
    获取加载器工厂单例
    
    Returns:
        LoaderFactory: 工厂实例
    """
    global _loader_factory
    if _loader_factory is None:
        _loader_factory = LoaderFactory()
    return _loader_factory
