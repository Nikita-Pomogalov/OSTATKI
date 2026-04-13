import customtkinter as ctk
import threading
from ui_components import MarketplacePanel
from market_apis import YandexMarketAPI, OzonAPI, WildberriesAPI


class MainApp(ctk.CTk):
    """Главное окно приложения"""

    def __init__(self):
        super().__init__()

        self.title("MP-Остатки")
        self.geometry("1100x600")
        self.resizable(False, False)

        # Центрируем окно
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (self.winfo_width() // 2)
        y = (self.winfo_screenheight() // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")

        # Сначала показываем текст загрузки
        self.loading_label = ctk.CTkLabel(
            self,
            text="Загрузка программы...\nПожалуйста, подождите 10-15 секунд",
            font=ctk.CTkFont(size=20),
            text_color="#888888"
        )
        self.loading_label.pack(expand=True)

        # Обновляем окно, чтобы текст появился сразу
        self.update()

        # Запускаем инициализацию в отдельном потоке
        threading.Thread(target=self.init_app, daemon=True).start()

    def init_app(self):
        """Инициализация приложения (в фоне)"""

        # Создаём API-клиенты
        yandex_api = YandexMarketAPI(
            campaign_id="148729186",
            api_key="ACMA:YQwxxaomrWOiUQ0PEkfXnDtFcNiBCxzg5WeN6FfU:b2a295f7"
        )

        ozon_api = OzonAPI(
            client_id="3596333",
            api_key="d1959905-e902-42e8-91bd-d4f68b103f0f"
        )

        wb_api = WildberriesAPI(
            api_key="eyJhbGciOiJFUzI1NiIsImtpZCI6IjIwMjYwMzAydjEiLCJ0eXAiOiJKV1QifQ.eyJhY2MiOjMsImVudCI6MSwiZXhwIjoxNzkxNjU4NTczLCJmb3IiOiJzZWxmIiwiaWQiOiIwMTlkN2I1My1hYTcwLTcyMzktYjVlNi1kMGIxZWM2NjllNTAiLCJpaWQiOjgxODkzOTEsIm9pZCI6NDM4ODgzOCwicyI6ODE2NjIsInNpZCI6IjU4NWViMzcyLTVhZWYtNDE2Zi05ZDkyLTc2NDZlNmZiNTc5OCIsInQiOmZhbHNlLCJ1aWQiOjgxODkzOTF9.4B11lMuqjHNTy0rd879nPRKCK_AxUGgHcEfqqFuv7xa4ZEwyioZVcarMkuRmXpybF2T0_XPx3bCQuaW6Yqjuug"
        )

        # Создаём интерфейс (в основном потоке)
        self.after(0, lambda: self.create_ui(yandex_api, ozon_api, wb_api))

    def create_ui(self, yandex_api, ozon_api, wb_api):
        """Создание интерфейса"""

        # Убираем текст загрузки
        self.loading_label.destroy()

        # Основной контейнер
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Три колонки
        self.yandex_panel = MarketplacePanel(
            main_frame, "ЯНДЕКС-МАРКЕТ",
            yandex_api,
            cooldown_seconds=0,
            width=320, height=500
        )
        self.yandex_panel.pack(side="left", padx=5, fill="both", expand=True)

        self.ozon_panel = MarketplacePanel(
            main_frame, "ОЗОН",
            None, api_client_ozon=ozon_api,
            cooldown_seconds=0,
            width=320, height=500
        )
        self.ozon_panel.pack(side="left", padx=5, fill="both", expand=True)

        self.wb_panel = MarketplacePanel(
            main_frame, "WILDBERRIES",
            None, api_client_wb=wb_api,
            cooldown_seconds=20,
            width=320, height=500
        )
        self.wb_panel.pack(side="left", padx=5, fill="both", expand=True)

        # Автозагрузка данных
        self.after(500, self.auto_load)

    def auto_load(self):
        """Автоматическая загрузка при старте"""
        self.yandex_panel.update_stocks()
        self.ozon_panel.update_stocks()
        self.after(2000, lambda: self.wb_panel.update_stocks())


if __name__ == "__main__":
    app = MainApp()
    app.mainloop()