from prettytable import PrettyTable

class Aligner():

    def __init__(self, original, toalign) -> None:
        self.original = original
        self.toalign = toalign
        self.table = PrettyTable()

        self.table.field_names = ["Orginal", "Index", "Translated"]
        self.table.align["Orginal"] = "l"
        self.table.align["Translated"] = "l"
        self.table.max_width["Orginal"] = 60
        self.table.max_width["Translated"] = 60


    def print_table(self):
        self.table.clear_rows()
        for index, value in enumerate(self.original):
            original_text = value
            if len(self.toalign) > index:
                toalign_text = self.toalign[index]
            else:
                toalign_text = ""

            self.table.add_row([original_text, index, toalign_text])

        print(self.table)

    def shift_lines(self, index):
        if self.toalign[index] == "":
            del self.toalign[index]
        else:
            self.toalign.insert(index, "")

    def align(self):
        while True:
            self.print_table()
            userInput = input("Insert empty line at:")
            try:
                index = int(userInput)
                self.shift_lines(index)
                continue

            except ValueError:
                print("Save")
                break

        return self.toalign
