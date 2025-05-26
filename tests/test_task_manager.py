# úkol používá dvě databáze:
# - 'task_manager' 
# - 'task_manager_test' pro testování
#
# CREATE DATABASE task_manager;
# CREATE DATABASE task_manager_test;


from src.task_manager import pridat_ukol, aktualizovat_ukol, smazat_ukol, zobrazit_ukoly, pripojeni_db, vytvoreni_tabulky
import mysql.connector
from mysql.connector import Error
import pytest

# připojení k testovací databázi
@pytest.fixture
def test_connection():
    conn = pripojeni_db(test=True)  
    vytvoreni_tabulky(conn)

# vymázání tabulky před testem
    cursor = conn.cursor()
    cursor.execute("DELETE FROM ukoly")
    conn.commit()
    yield conn
    conn.close()

# test přidání úkolu - pozitivní
def test_pridat_ukol_positive(monkeypatch, test_connection):
    input_values = iter(["test ukol", "test popis"])
    monkeypatch.setattr("builtins.input", lambda _: next(input_values))
    pridat_ukol(test_connection)

    cursor = test_connection.cursor()
    cursor.execute("SELECT * FROM ukoly WHERE task_name = %s", ("test ukol",))
    result = cursor.fetchone()
    assert result is not None
    assert result[1] == "test ukol"
    assert result[2] == "test popis"

    cursor.execute("DELETE FROM ukoly WHERE task_name = %s", ("test ukol",))
    test_connection.commit()

# přidání úkolu - negativní
def test_pridat_ukol_negative(monkeypatch, test_connection):
    input_values = iter(["", "test popis"])
    monkeypatch.setattr("builtins.input", lambda _: next(input_values))

    try:
        pridat_ukol(test_connection)
    except IndexError:
        pass 
    except StopIteration:
        pass 

    cursor = test_connection.cursor()
    cursor.execute("SELECT * FROM ukoly WHERE description = %s", ("test popis",))
    result = cursor.fetchone()
    assert result is None

# test aktualizace úkolu- pozitivní
def test_aktualizovat_ukol_positive(monkeypatch, test_connection):
    cursor = test_connection.cursor()
    cursor.execute("INSERT INTO ukoly (task_name, description, stav) VALUES (%s, %s, %s)", 
                ("test_ukol", "popis", "Nezahájeno"))
    test_connection.commit()
    cursor.execute("SELECT id FROM ukoly WHERE task_name = %s", ("test_ukol",))
    task_id = cursor.fetchone()[0]

    input_values = iter([str(task_id), "Hotovo"])
    monkeypatch.setattr("builtins.input", lambda _: next(input_values))

    aktualizovat_ukol(test_connection)
    cursor.execute("SELECT stav FROM ukoly WHERE id = %s", (task_id,))
    stav = cursor.fetchone()[0]
    assert stav == "Hotovo"

    cursor.execute("DELETE FROM ukoly WHERE id = %s", (task_id,))
    test_connection.commit()

# test aktualizace úkolu- negativní
def test_aktualizace_ukolu_negative(monkeypatch, test_connection):
    cursor = test_connection.cursor()
    cursor.execute("INSERT INTO ukoly (task_name, description, stav) VALUES (%s, %s, %s)", 
                ("test_ukol", "test_popis", "Nezahájeno"))
    test_connection.commit()
    cursor.execute("SELECT id FROM ukoly WHERE task_name = %s", ("test_ukol",))
    task_id = cursor.fetchone()[0]

    input_values = iter([str(task_id), "neplatné"])
    monkeypatch.setattr("builtins.input", lambda _: next(input_values))

    aktualizovat_ukol(test_connection)
    cursor.execute("SELECT stav FROM ukoly WHERE id = %s", (task_id,))
    stav = cursor.fetchone()[0]
    assert stav == "Nezahájeno"

    cursor.execute("DELETE FROM ukoly WHERE id = %s", (task_id,))
    test_connection.commit()

# test odstranění úkolu - pozitivní
def test_odstraneni_ukolu_positive(monkeypatch, test_connection):
    cursor = test_connection.cursor()
    cursor.execute("INSERT INTO ukoly (task_name, description, stav) VALUES (%s, %s, %s)", 
                ("test_ukol", "test_popis", "Nezahájeno"))
    test_connection.commit()
    cursor.execute("SELECT id FROM ukoly WHERE task_name = %s", ("test_ukol",))
    task_id = cursor.fetchone()[0]

    input_values = iter([str(task_id)])
    monkeypatch.setattr("builtins.input", lambda _: next(input_values))

    smazat_ukol(test_connection)
    cursor.execute("SELECT id FROM ukoly WHERE task_name = %s", ("test_ukol",))
    task_id = cursor.fetchone()
    assert task_id is None

# test odstranění úkolu - negativní
def test_odstraneni_ukolu_negative(monkeypatch, test_connection, capsys):
    cursor = test_connection.cursor()
    cursor.execute("INSERT INTO ukoly (task_name, description, stav) VALUES (%s, %s, %s)", 
                ("test_ukol", "test_popis", "Nezahájeno"))
    test_connection.commit()
    cursor.execute("SELECT id FROM ukoly WHERE task_name = %s", ("test_ukol",))
    test_id = cursor.fetchone()[0]

    test_id = 9999
    while True:
        cursor.execute("SELECT id FROM ukoly WHERE id = %s", (test_id,))
        if cursor.fetchone() is None:
            break
        test_id += 1 

    input_values = iter([str(test_id)])
    monkeypatch.setattr("builtins.input", lambda _: next(input_values))

    smazat_ukol(test_connection)
    captured = capsys.readouterr()
    assert "Úkol s tímto ID neexistuje." in captured.out
    cursor.execute("SELECT id FROM ukoly WHERE task_name = %s", ("test_ukol",))
    task = cursor.fetchone()
    assert task is not None

    cursor.execute("DELETE FROM ukoly WHERE task_name = %s", ("test_ukol",))
    test_connection.commit()
