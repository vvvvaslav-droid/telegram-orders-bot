from gc import callbacks

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler, ContextTypes, CallbackQueryHandler
import sqlite3

key=''
password='7428'
NAME,PHONE=range(2)

async def start(update:Update,context:ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Введите имя")
    return NAME

async def nameing(update:Update,contexn:ContextTypes.DEFAULT_TYPE):
    try:
        text = update.message.text
        if  text == password:
            keyboards=[
                [InlineKeyboardButton("Заявки", callback_data='show_orders')],
                [InlineKeyboardButton("Очистить базу",callback_data='clear_db')]
            ]
            reply_markup= InlineKeyboardMarkup(keyboards)
            await update.message.reply_text("Админ понель:",reply_markup=reply_markup)
            return ConversationHandler.END
        contexn.user_data["name"]=text
        await update.message.reply_text("Введите номер телефона")
        return PHONE
    except Exception as e:
        print(f'ошибка:{e}')
        await update.message.reply_text("Ошибка")
        return NAME

def sbor():
    file=sqlite3.connect("orders.db")
    cursor=file.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS orders(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    username TEXT,
    name TEXT,
    phone TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)
    """)
    file.commit()
    file.close()

async def phone_name(update:Update, context:ContextTypes.DEFAULT_TYPE):
    try:
        phone= update.message.text
        name= context.user_data["name"]
        user_id,username=update.effective_user.id,update.effective_user.username or "Нет username"
        file =sqlite3.connect("orders.db")
        cursors= file.cursor()
        cursors.execute("""
        INSERT INTO orders(user_id,username,name,phone)
        VALUES (?,?,?,?)""",(user_id,username,name,phone))
        file.commit()
        file.close()
        await update.message.reply_text("Заявка обработана")
        return ConversationHandler.END
    except Exception as e:
        print(f"error:{e}")
        await update.message.reply_text("Ошибка")
        return PHONE
async def button_handler(update:Update, context:ContextTypes.DEFAULT_TYPE):
    try:
        query= update.callback_query
        await query.answer()
        if query.data== 'show_orders':
            file=sqlite3.connect("orders.db")
            cursor = file.cursor()
            cursor.execute("SELECT * FROM orders ORDER BY created_at DESC")
            orders= cursor.fetchall()
            file.close()
            if orders:
                text='Список заявок:\n\n'
                for order in orders:
                    text+= f"#{order[0]}|{order[3]}|{order[4]}|{order[2] or 'нет username'}\n"
                await query.message.reply_text(text)
                keyboards = [
                    [InlineKeyboardButton("Заявки", callback_data='show_orders')],
                    [InlineKeyboardButton("Очистить базу", callback_data='clear_db')]
                ]
                reply_markup = InlineKeyboardMarkup(keyboards)
                await query.message.reply_text("Админ понель:", reply_markup=reply_markup)

            else:
                await query.message.reply_text('заявок пока нет')
                keyboards = [
                    [InlineKeyboardButton("Заявки", callback_data='show_orders')],
                    [InlineKeyboardButton("Очистить базу", callback_data='clear_db')]
                ]
                reply_markup = InlineKeyboardMarkup(keyboards)
                await query.message.reply_text("Админ понель:", reply_markup=reply_markup)
        elif query.data == 'clear_db':
            file = sqlite3.connect("orders.db")
            cursor=file.cursor()
            cursor.execute("DELETE FROM orders")
            file.commit()
            file.close()
            await query.message.reply_text("База удалена")
            keyboards = [
                [InlineKeyboardButton("Заявки", callback_data='show_orders')],
                [InlineKeyboardButton("Очистить базу", callback_data='clear_db')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboards)
            await query.message.reply_text("Админ понель:", reply_markup=reply_markup)
    except Exception as e:
        print(e)

def main():
    sbor()

    app=Application.builder().token(key).build()

    conv = ConversationHandler(
        entry_points=[CommandHandler("start",start)],
        states={
        NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, nameing)],
        PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, phone_name)],
        },
        fallbacks=[]
    )
    app.add_handler(conv)
    app.add_handler(CallbackQueryHandler(button_handler))
    app.run_polling()

if __name__=="__main__":
    main()