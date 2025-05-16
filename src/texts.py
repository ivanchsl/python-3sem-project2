from random import choice


start_generation_text = "Ожидайте, изображение генерируется..."
wait_texts = ["Ещё немного...", "Осталось совсем чуть-чуть...", "Минуточку терпения..."]
help_text = ("Бот обращается к нейросети Kandinsky для генерации изображения "
             "по заданному запросу. Для ввода запроса можно воспользоваться "
             "командой /input или выбрать соответствующий пункт на виртуальной "
             "клавиатуре.\n"
             "Также поддерживается выбор различных вариантов стиля изображения. "
             "Для выбора стиля можно воспользоваться командой /style или выбрать "
             "соответствующий пункт на виртуальной клавиатуре.")


def getWaitText(num: int) -> str:
    """
    Returns appropriate waiting message text based on iteration number.
    
    Args:
        num: Current iteration number in waiting loop
        
    Returns:
        str: Waiting message text to show
    """
    if num == 0:
        return start_generation_text
    return choice(wait_texts)
