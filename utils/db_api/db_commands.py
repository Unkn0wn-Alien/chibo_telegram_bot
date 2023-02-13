from typing import Union

import asyncpg
from asyncpg import Connection
from asyncpg.pool import Pool

from config import config


class Database:
    def __init__(self):
        self.pool: Union[Pool, None] = None

    async def create(self):
        self.pool = await asyncpg.create_pool(
            user=config.DB_USER,
            password=config.DB_PASS,
            host=config.DB_HOST,
            database=config.DB_NAME,
        )

    async def execute(
            self,
            command,
            *args,
            fetch: bool = False,
            fetchval: bool = False,
            fetchrow: bool = False,
            execute: bool = False,
    ):
        async with self.pool.acquire() as connection:
            connection: Connection
            async with connection.transaction():
                if fetch:
                    result = await connection.fetch(command, *args)
                elif fetchval:
                    result = await connection.fetchval(command, *args)
                elif fetchrow:
                    result = await connection.fetchrow(command, *args)
                elif execute:
                    result = await connection.execute(command, *args)
            return result

    @staticmethod
    def format_args(sql, parameters: dict):
        sql += " AND ".join(
            [f"{item} = ${num}" for num, item in enumerate(parameters.keys(), start=1)]
        )
        return sql, tuple(parameters.values())

    async def create_table_users(self):
        sql = """
        CREATE TABLE IF NOT EXISTS Users (
        id BIGSERIAL PRIMARY KEY NOT NULL,
        telegram_id BIGINT NOT NULL,
        full_name varchar (255) NOT NULL,
        language varchar (255) NOT NULL,
        phone_number varchar (255) NOT NULL,
        address_id varchar (255) NULL,
        created_at TIMESTAMP NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMP NULL DEFAULT NOW(),
        deleted_at TIMESTAMP DEFAULT NULL
        );
        """

        await self.execute(sql, execute=True)

    async def add_user(self, telegram_id, full_name, language, phone_number, address_id):
        sql = "INSERT INTO users (telegram_id, full_name, language, phone_number, address_id) VALUES ($1, $2, $3, $4, $5) RETURNING *"
        return await self.execute(sql, telegram_id, full_name, language, phone_number, address_id, fetchrow=True)

    async def select_user(self, **kwargs):
        sql = "SELECT * FROM users WHERE "
        sql, parameters = self.format_args(sql, parameters=kwargs)
        return await self.execute(sql, *parameters, fetchrow=True)

    async def select_user_id(self):
        sql = "SELECT telegram_id FROM users"
        return await self.execute(sql, fetch=True)

    async def select_language(self, telegram_id):
        sql = f"SELECT language FROM users WHERE telegram_id='{telegram_id}'"
        return await self.execute(sql, fetchrow=True)

    async def select_username(self, telegram_id):
        sql = f"SELECT full_name FROM users WHERE telegram_id='{telegram_id}'"
        return await self.execute(sql, fetchrow=True)

    async def select_phone_number(self, telegram_id):
        sql = "SELECT phone_number FROM users WHERE telegram_id=$1"
        return await self.execute(sql, telegram_id, fetchrow=True)

    async def count_users(self):
        sql = "SELECT COUNT(*) FROM users"
        return await self.execute(sql, fetchval=True)

    async def update_user_language(self, language_user, telegram_id):
        sql = "UPDATE users SET language=$1 WHERE telegram_id=$2"
        return await self.execute(sql, language_user, telegram_id, execute=True)

    async def update_user_phone_number(self, phone_number, telegram_id):
        sql = "UPDATE users SET phone_number=$1 WHERE telegram_id=$2"
        return await self.execute(sql, phone_number, telegram_id, execute=True)

    async def update_user_fullname(self, full_name, telegram_id):
        sql = "UPDATE users SET full_name=$1 WHERE telegram_id=$2"
        return await self.execute(sql, full_name, telegram_id, execute=True)

    async def create_table_feedbacks(self):
        sql = """
                CREATE TABLE IF NOT EXISTS Feedbacks (
                id BIGSERIAL PRIMARY KEY NOT NULL,
                name VARCHAR (255) NOT NULL,
                feedback VARCHAR (255) NULL
                );
                """
        await self.execute(sql, execute=True)

    async def add_feedback(self, name, feedback):
        sql = "INSERT INTO feedbacks (name, feedback) VALUES ($1, $2) RETURNING *"
        return await self.execute(sql, name, feedback, fetchrow=True)

    async def create_table_category(self):
        sql = """
                CREATE TABLE IF NOT EXISTS Category_rus (
                id BIGSERIAL PRIMARY KEY NOT NULL,
                category_name_uz VARCHAR(255) NOT NULL,
                category_name_ru VARCHAR(255) NOT NULL,
                photo varchar(255) NULL,
                created_at TIMESTAMP NOT NULL DEFAULT NOW(),
                updated_at TIMESTAMP NULL DEFAULT NOW(),
                deleted_at TIMESTAMP DEFAULT NULL
                );
                """
        await self.execute(sql, execute=True)

    async def get_categories_by_id_uz(self, category_name_uz):
        sql = "SELECT id FROM Category_rus WHERE category_name_uz=$1"
        return await self.execute(sql, category_name_uz, fetch=True)

    async def get_categories_by_id_ru(self, category_name_ru):
        sql = "SELECT id FROM Category_rus WHERE category_name_ru=$1"
        return await self.execute(sql, category_name_ru, fetch=True)

    async def get_categories_uz(self):
        sql = "SELECT category_name_uz FROM Category_rus"
        return await self.execute(sql, fetch=True)

    async def get_categories_ru(self):
        sql = "SELECT category_name_ru FROM Category_rus"
        return await self.execute(sql, fetch=True)

    async def create_table_products(self):
        sql = """
                CREATE TABLE IF NOT EXISTS Product_rus (
                id BIGSERIAL PRIMARY KEY NOT NULL,
                product_name_uz VARCHAR (255) NOT NULL,
                product_name_ru VARCHAR (255) NOT NULL,
                foto VARCHAR (255) NULL DEFAULT NULL,
                price INTEGER NOT NULL,
                quantity INTEGER NULL DEFAULT NULL,
                soft_delete VARCHAR (255) NULL DEFAULT NULL,
                description_uz TEXT NULL DEFAULT NULL,
                description_ru TEXT NULL DEFAULT NULL,
                parent_id INTEGER NULL DEFAULT '0',
                created_at TIMESTAMP NOT NULL DEFAULT NOW(),
                updated_at TIMESTAMP NULL DEFAULT NULL,
                deleted_at TIMESTAMP DEFAULT NULL,
                category_id INTEGER NULL NOT NULL,
                CONSTRAINT fk_category FOREIGN KEY (category_id) REFERENCES category_rus (id)
                );
                """
        await self.execute(sql, execute=True)

    async def get_products(self, category_id):
        sql = f"SELECT * FROM Product_rus WHERE category_id='{category_id}'"
        return await self.execute(sql, fetch=True)

    async def get_product_by_id_uz(self, product_name_uz):
        sql = "SELECT id FROM Product_rus WHERE product_name_uz=$1"
        return await self.execute(sql, product_name_uz, fetch=True)

    async def get_product_by_id_ru(self, product_name_ru):
        sql = "SELECT id FROM Product_rus WHERE product_name_ru=$1"
        return await self.execute(sql, product_name_ru, fetch=True)

    async def get_product(self, id):
        sql = f"SELECT * FROM Product_rus WHERE id='{id}'"
        return await self.execute(sql, fetchrow=True)

    async def create_table_cart(self):
        sql = """
                CREATE TABLE IF NOT EXISTS Cart (
                id BIGSERIAL PRIMARY KEY NOT NULL,
                product_name varchar(255) NOT NULL,
                price INTEGER NOT NULL,
                quantity INTEGER NULL,
                telegram_id BIGINT NOT NULL,
                product_id INTEGER NOT NULL,
                created_at TIMESTAMP NOT NULL DEFAULT NOW(),
                updated_at TIMESTAMP NULL DEFAULT NOW(),
                deleted_at TIMESTAMP DEFAULT NULL
                );
                """
        await self.execute(sql, execute=True)

    async def add_cart(self, product_name, price, quantity, product_id, telegram_id):
        sql = "INSERT INTO Cart (product_name, price, quantity, product_id, telegram_id) VALUES($1, $2, $3, $4, $5) returning *"
        return await self.execute(sql, product_name, price, quantity, product_id, telegram_id,
                                  fetchrow=True)

    async def select_cart(self, telegram_id):
        sql = f"SELECT * FROM Cart WHERE telegram_id={telegram_id}"
        return await self.execute(sql, fetch=True)

    async def select_cart_if_exist(self, product_id, telegram_id):
        sql = f"SELECT * FROM Cart WHERE product_id={product_id} AND telegram_id={telegram_id}"
        return await self.execute(sql, fetch=True)

    async def get_cart(self):
        sql = "SELECT DISTINCT product_id FROM Cart"
        return await self.execute(sql, fetch=True)

    async def delete_cart(self, telegram_id):
        sql = f"DELETE FROM Cart WHERE telegram_id={telegram_id}"
        return await self.execute(sql, execute=True)

    async def update_product_quantity(self, quantity, product_id, telegram_id):
        sql = f"UPDATE Cart SET quantity={quantity} WHERE product_id={product_id} AND telegram_id={telegram_id}"
        return await self.execute(sql, execute=True)

    async def create_table_addresses(self):
        sql = """
                CREATE TABLE IF NOT EXISTS Address (
                id BIGSERIAL PRIMARY KEY NOT NULL,
                address VARCHAR(255) NULL,
                long VARCHAR(255) NULL,
                lat VARCHAR(255) NULL,
                telegram_id BIGINT NULL,
                created_at TIMESTAMP NULL DEFAULT NOW(),
                updated_at TIMESTAMP NULL DEFAULT NOW(),
                deleted_at TIMESTAMP DEFAULT NULL
                );
                """
        await self.execute(sql, execute=True)

    async def add_address(self, address, long, lat, telegram_id):
        sql = "INSERT INTO Address (address, long, lat, telegram_id) VALUES($1, $2, $3, $4) returning *"
        return await self.execute(sql, address, long, lat, telegram_id,
                                  fetchrow=True)

    async def select_address(self, telegram_id):
        sql = f"SELECT * FROM Address WHERE telegram_id={telegram_id}"
        return await self.execute(sql, fetch=True)

    async def create_table_orders(self):
        sql = """
                CREATE TABLE IF NOT EXISTS Orders (
                id BIGSERIAL PRIMARY KEY NOT NULL,
                order_code varchar (255) NOT NULL,
                telegram_id BIGINT NOT NULL,
                created_at TIMESTAMP NOT NULL DEFAULT NOW(),
                update_at TIMESTAMP NULL DEFAULT NOW(),
                deleted_at TIMESTAMP DEFAULT NULL
                );
                """
        await self.execute(sql, execute=True)

    async def add_order(self, order_code, telegram_id):
        sql = "INSERT INTO orders (order_code, telegram_id) VALUES ($1, $2) returning *"
        return await self.execute(sql, order_code, telegram_id, fetchrow=True)

    async def select_order(self, telegram_id):
        sql = f"SELECT * FROM orders WHERE telegram_id={telegram_id}"
        return await self.execute(sql, fetch=True)

    async def select_order_by_id(self, telegram_id):
        sql = f"SELECT id FROM orders WHERE telegram_id={telegram_id}"
        return await self.execute(sql, fetch=True)

    async def create_table_orders_ontime(self):
        sql = """
                CREATE TABLE IF NOT EXISTS Orders_ontime (
                id BIGSERIAL PRIMARY KEY NOT NULL,
                order_code varchar (255) NOT NULL,
                product_name varchar(255) NOT NULL,
                product_id INTEGER NOT NULL,
                price INTEGER NOT NULL,
                quantity INTEGER NOT NULL,
                telegram_id BIGINT NOT NULL,
                phone_number varchar (255) NOT NULL,
                created_at TIMESTAMP NOT NULL DEFAULT NOW(),
                update_at TIMESTAMP NULL DEFAULT NOW(),
                deleted_at TIMESTAMP DEFAULT NULL
                );
                """
        await self.execute(sql, execute=True)

    async def add_order_ontime(self, order_code, product_name, product_id, price, quantity, telegram_id, phone_number):
        sql = "INSERT INTO orders_ontime (order_code, product_name, product_id, price, quantity, telegram_id, phone_number) VALUES ($1, $2, $3, $4, $5, $6, $7) returning *"
        return await self.execute(sql, order_code, product_name, product_id, price, quantity, telegram_id, phone_number,
                                  fetchrow=True)

    async def select_order_ontime(self, telegram_id):
        sql = f"SELECT * FROM orders_ontime WHERE telegram_id={telegram_id}"
        return await self.execute(sql, fetch=True)

    async def delete_order_ontime(self, telegram_id):
        sql = f"DELETE FROM orders_ontime WHERE telegram_id={telegram_id}"
        return await self.execute(sql, execute=True)

    async def create_table_orders_details(self):
        sql = """
                CREATE TABLE IF NOT EXISTS Orders_details (
                id BIGSERIAL PRIMARY KEY NOT NULL,
                order_id BIGINT NOT NULL,
                product_id BIGINT NOT NULL,
                quantity INTEGER NOT NULL,
                created_at TIMESTAMP NOT NULL DEFAULT NOW(),
                updated_at TIMESTAMP NULL DEFAULT NOW(),
                deleted_at TIMESTAMP DEFAULT NULL
                );
                """
        await self.execute(sql, execute=True)

    async def add_order_details(self, order_id, product_id, quantity):
        sql = "INSERT INTO orders_details (order_id, product_id, quantity) VALUES ($1, $2, $3) returning *"
        return await self.execute(sql, order_id, product_id, quantity,
                                  fetchrow=True)

    async def create_table_orders_for_user(self):
        sql = """
                CREATE TABLE IF NOT EXISTS Orders_for_user (
                id BIGSERIAL PRIMARY KEY NOT NULL,
                order_code varchar (255) NOT NULL,
                product_name varchar(255) NOT NULL,
                price INTEGER NOT NULL,
                quantity INTEGER NOT NULL,
                telegram_id BIGINT NOT NULL,
                phone_number varchar (255) NOT NULL,
                created_at TIMESTAMP NOT NULL DEFAULT NOW(),
                updated_at TIMESTAMP NULL DEFAULT NOW(),
                deleted_at TIMESTAMP DEFAULT NULL
                );
                """
        await self.execute(sql, execute=True)

    async def add_orders_for_user(self, order_code, product_name, price, quantity, telegram_id, phone_number):
        sql = "INSERT INTO orders_for_user (order_code, product_name, price, quantity, telegram_id, phone_number) VALUES ($1, $2, $3, $4, $5, $6) returning *"
        return await self.execute(sql, order_code, product_name, price, quantity, telegram_id, phone_number,
                                  fetchrow=True)

    async def select_orders_for_user(self, telegram_id):
        sql = f"SELECT * FROM orders_for_user WHERE telegram_id={telegram_id}"
        return await self.execute(sql, fetch=True)
