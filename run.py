from wordly1 import bot
import logging
import signal
import sys

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Флаг для отслеживания состояния бота
is_running = True

def signal_handler(sig, frame):
    global is_running
    logger.info("Получен сигнал завершения (Ctrl+C). Завершаем работу бота...")
    is_running = False
    bot.stop_polling()
    sys.exit(0)

def main():
    try:
        # Устанавливаем обработчик сигнала SIGINT (Ctrl+C)
        signal.signal(signal.SIGINT, signal_handler)
        
        logger.info("Starting Wordly bot...")
        bot.polling(none_stop=True)
    except Exception as e:
        logger.error(f"Error occurred: {e}")
    finally:
        logger.info("Bot stopped")

if __name__ == "__main__":
    main() 