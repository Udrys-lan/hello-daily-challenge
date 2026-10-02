from main import UserManager

def run_test():
    print("====测试增删改查====")
    um = UserManager()
    print(um.add_user("张三", 18))
    print(um.add_user("李四", 20))

    print("get_user(1):", um.get_user(1))
    print("get_user(99):", um.get_user(99))

    print("update_age(1,19):", um.update_age(1,19))
    print("remove_user(2):", um.remove_user(2))
    print("remove_user(2)再次:", um.remove_user(2))

    print("list_users:", um.list_users())

    print("\n====测试持久化保存加载====")
    um.save_to_json("users.json")

    um2 = UserManager()
    um2.load_from_json("users.json")
    print("um2 list_users:", um2.list_users())
    # 验证加载后id接续：现有最大id=1，新增应该id=2
    print("um2 add_user(王五,22):", um2.add_user("王五",22))

if __name__ == "__main__":
    run_test()
