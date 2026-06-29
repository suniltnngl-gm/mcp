class Greeter:
    def __init__(self, name):
        self.name = name

    def greet(self):
        print(f"Hello, {self.name}!")

def say_hello(name):
    greeter = Greeter(name)
    greeter.greet()

if __name__ == "__main__":
    say_hello("World")
