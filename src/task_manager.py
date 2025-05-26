import mysql.connector
from mysql.connector import Error

def pripojeni_db(test=False):
    try:
        database_name = 'task_manager_test' if test else 'task_manager'
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='1111',  
            database= database_name
        )
        if connection.is_connected():
            print("Úspěšně připojeno k databázi.")
            return connection
    except Error as e:
        print(f"Chyba při připojení k databázi: {e}")
        return None
    
def vytvoreni_tabulky(connection):
    try:
        cursor = connection.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ukoly (
                id INT AUTO_INCREMENT PRIMARY KEY,
                task_name VARCHAR(100) NOT NULL,
                description VARCHAR(100) NOT NULL,
                stav ENUM('Nezahájeno', 'Probíhá', 'Hotovo') DEFAULT 'Nezahájeno'
            );
        """)
        connection.commit()
        print("Tabulka ukoly byla vytvořena nebo již existuje.")
    except Error as e:
        print(f"Chyba při vytváření tabulky: {e}")


# TASK MANAGER

# fukce
# spuštění menu
def hlavni_menu():

    connection = pripojeni_db()
    if not connection:
        return
    vytvoreni_tabulky(connection)

    while True:
        print('\nSprávce úkolů - Hlavní menu\n 1. Přidat nový úkol\n 2. Zobrazit všechny úkoly\n 3. Aktualizovat úkol\n 4. Odstranit úkol \n 5. Konec programu')
        user_choice = input('Vyberte možnost (1 - 5): ')

        if user_choice == "1":
            pridat_ukol(connection)
        elif user_choice == "2":
            zobrazit_ukoly(connection)
        elif user_choice == "3":
            aktualizovat_ukol(connection)
        elif user_choice == "4":
            smazat_ukol(connection)
        elif user_choice == "5":
            print('Konec programu.')
            break
        else:
            print('Zadejte číslo 1 - 5.')

# 1. přidat úkol
def pridat_ukol(connection):
    while True:
        task_name = input('Přidat úkol: ').strip()

        if task_name == "":
            print('Úkol musí mít název. Zadejte název úkolu.')
            continue
        if len(task_name) > 100:
            print("Název úkolu je příliš dlouhý (max. 100 znaků). Zadej kratší název.")
            continue
        if ukol_existuje(task_name, connection):
            print('Úkol již existuje!')
            continue
        else:
            break

# přidání popisu
    description = input('Přidejte popis k úkolu (nepovinné): ').strip()
    if description == "":
        description = 'Úkol nemá popis.'
    elif len(description) > 100:
        print("Popis je příliš dlouhý (max 100 znaků). Bude zkrácen.")
        description = description[:100]

# přidání do databáze
    try:
        cursor = connection.cursor()
        cursor.execute("INSERT INTO ukoly (task_name, description) VALUES (%s, %s)", (task_name, description))
        connection.commit()
        print("Úkol byl úspěšně přidán.")
    except Error as e:
        print(f"Chyba při přidávání úkolu: {e}")

# 2. zobrazit úkoly
def zobrazit_ukoly(connection):
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT id, task_name, description, stav FROM ukoly WHERE stav IN ('Nezahájeno', 'Probíhá')")
        ukoly = cursor.fetchall()
        if not ukoly:
            print("Žádné úkoly.")
            return
        print('\nTvoje úkoly: ')
        for task in ukoly:
            print(f"ID: {task[0]}, Název: {task[1]}, Popis: {task[2]}, Stav: {task[3]}")
    except Error as e:
        print(f"Chyba při načítání úkolů: {e}")

# 3. aktializovat úkol
def aktualizovat_ukol(connection):
    zobrazit_ukoly(connection)
    try:
        task_id = int(input("Zadej ID úkolu ke změně stavu: "))
    except ValueError:
        print("Neplatné ID.")
        return
    
    novy_stav = input("Zadej nový stav (Probíhá/Hotovo): ").capitalize()
    if novy_stav not in ["Probíhá", "Hotovo"]:
        print("Neplatný stav.")
        return
    
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM ukoly WHERE id = %s", (task_id,))
        if cursor.fetchone() is None:
            print("Úkol s tímto ID neexistuje.")
            return
        
        cursor.execute("UPDATE ukoly SET stav = %s WHERE id = %s", (novy_stav, task_id))
        connection.commit()
        print("Stav úkolu byl aktualizován.")
    except Error as e:
        print(f"Chyba při aktualizaci: {e}")

# 4. odstranit úkol
def smazat_ukol(connection):
    zobrazit_ukoly(connection)
    task_number = valid_number()

    try:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM ukoly WHERE id = %s", (task_number,))
        if cursor.fetchone() is None:
            print("Úkol s tímto ID neexistuje.")
            return

        cursor.execute("DELETE FROM ukoly WHERE id = %s", (task_number,))
        connection.commit()
        print("Úkol byl odstraněn.")
    except Error as e:
        print(f"Chyba při mazání: {e}")

# kontrola inputu 
def valid_number():
    while True:
        num_input = input('Zadejte ID úkolu k odstranění: ')
        try:
            number = int(num_input)
            if 1 <= number:
                return number
            else:
                print("ID úkolu není platné.")
        except ValueError:
            print("Zadejte platné číslo ID.")

# kontrola duplicity 
def ukol_existuje(task_name, connection):
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM ukoly WHERE task_name = %s", (task_name,))
    result = cursor.fetchone()
    return result is not None

# spuštění programu
if __name__ == "__main__":
    hlavni_menu()