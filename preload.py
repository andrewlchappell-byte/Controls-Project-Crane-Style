def main():
    # open up the load file
    with open("load.py", "w") as load:
        
        load.write("""with open("main.py","w") as f: f.write(r\"\"\"""")
        with open("main.py", "r") as main:load.write(main.read())
        load.write("\"\"\")\n\n")

        load.write("""with open("boot.py","w") as f: f.write(r\"\"\"""")
        with open("boot.py", "r") as boot:load.write(boot.read())
        load.write("\"\"\")")
main()