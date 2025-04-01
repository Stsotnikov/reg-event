from dataclasses import dataclass
from typing import Optional
from environs import Env



@dataclass
class TgBot:
    token: str  # Токен для доступа к телеграм-боту

@dataclass
class PayToken:
    token: str
@dataclass
class PaysToken:
    token: PayToken
@dataclass
class Config:
    tg_bot: TgBot

# Создаем функцию, которая будет читать файл .env и возвращать экземпляр
# класса Config с заполненными полями token и admin_ids
def load_config(path: Optional[str] = None) -> Config:
    env = Env()
    env.read_env(path)
    return Config(tg_bot=TgBot(token=env('BOT_TOKEN')))

def load_pay_token(path: Optional[str] = None) -> PaysToken:
    env = Env()
    env.read_env(path)
    return PaysToken(token=PayToken(token=env('PAYMENT_TOKEN')))