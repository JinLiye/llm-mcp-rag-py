from rich.console import Console

console = Console()

def log_title(message: str) -> None:
    """
    打印一个居中的标题，两边用等号填充
    
    Args:
        message: 要显示的标题文本
    """
    total_length = 80
    message_length = len(message)
    padding = max(0, total_length - message_length - 4)  # 4 for spaces and "="
    
    left_padding = '=' * (padding // 2)
    right_padding = '=' * ((padding + 1) // 2)  # 向上取整
    
    padded_message = f"{left_padding} {message} {right_padding}"
    
    # 使用 rich 的样式标记
    console.print(f"[bold cyan]{padded_message}[/bold cyan]")
