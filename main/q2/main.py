import json

class UserManager:
    def __init__(self):
        self.users = []   # 保存用户，维持添加顺序，元素为用户字典
        self._next_id = 1 # 待分配的下一个id

    def add_user(self, name: str, age: int) -> dict:
        """添加用户，自动分配id，返回用户字典"""
        user = {
            "id": self._next_id,
            "name": name,
            "age": age
        }
        self.users.append(user)
        self._next_id += 1
        return user

    def get_user(self, user_id: int):
        """按id查询用户，无则返回None"""
        for u in self.users:
            if u["id"] == user_id:
                return u
        return None

    def update_age(self, user_id: int, new_age: int) -> bool:
        """修改用户年龄，成功True，不存在False"""
        user = self.get_user(user_id)
        if user is None:
            return False
        user["age"] = new_age
        return True

    def remove_user(self, user_id: int) -> bool:
        """删除用户，成功True，不存在False"""
        for idx, u in enumerate(self.users):
            if u["id"] == user_id:
                self.users.pop(idx)
                return True
        return False

    def list_users(self) -> list:
        """返回全部用户，保留添加顺序"""
        return self.users.copy()

    def save_to_json(self, filepath: str) -> None:
        """保存全部用户到json文件"""
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.users, f, ensure_ascii=False)

    def load_from_json(self, filepath: str) -> None:
        """加载json，覆盖当前数据；更新_next_id为最大id+1；文件不存在会抛json读取异常"""
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.users = data
        if len(self.users) > 0:
            # 取现有最大id，下一个id = max_id +1
            max_id = max(u["id"] for u in self.users)
            self._next_id = max_id + 1
        else:
            self._next_id = 1
