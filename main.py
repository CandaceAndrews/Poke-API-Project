import sqlite3
import requests


def create_tables(cur):
    """create all tables
    """
    create_pokemon_table(cur)
    create_move_table(cur)
    create_type_table(cur)
    create_pokemon_move_table(cur)
    create_pokemon_type_table(cur)


def create_pokemon_table(cur):
    """creates pokemon table
    """
    cur.execute("""
    CREATE TABLE IF NOT EXISTS POKEMON (
        NAME text UNIQUE,
        ID INT UNIQUE,
        PICTURE text UNIQUE
    )"""
                )


def create_move_table(cur):
    """creates the move table
    """
    cur.execute("""
    CREATE TABLE IF NOT EXISTS MOVE (
        MOVE_NAME text UNIQUE,
        MOVE_ID INT UNIQUE
    )"""
                )


def create_type_table(cur):
    """creates the type table
    """
    cur.execute("""
    CREATE TABLE IF NOT EXISTS TYPE (
        TYPE_NAME text UNIQUE,
        TYPE_ID INT UNIQUE
    )"""
                )


def create_pokemon_move_table(cur):
    """creates the pokemon + move table
    """
    cur.execute("""
    CREATE TABLE IF NOT EXISTS POKEMON_MOVE (
        POKEMON_NAME text,
        MOVE_NAME text
    )"""
                )


def create_pokemon_type_table(cur):
    """creates the pokemon + type table
    """
    cur.execute("""
    CREATE TABLE IF NOT EXISTS POKEMON_TYPE (
        POKEMON_NAME text,
        TYPE_NAME text
    )"""
                )


def drop_tables(cur, con):
    """deletes the tables
    """
    cur.execute("DROP TABLE POKEMON")
    cur.execute("DROP TABLE MOVE")
    cur.execute("DROP TABLE TYPE")
    cur.execute("DROP TABLE POKEMON_MOVE")
    cur.execute("DROP TABLE POKEMON_TYPE")
    con.commit()


def get_pokemon_api_data(base_url, pokemon):
    """returns json of API results for pokemon
    """
    # gets API info
    url = f"{base_url}/pokemon/{pokemon}"
    response = requests.get(url)
    return response.json()


def check_for_and_add_to_pokemon_table(cur, con, pokemon_name, pokemon_id, pokemon_sprite):
    """check for pokemon in database and add if not there
    """
    pokemon_query = f"""
    INSERT OR IGNORE INTO POKEMON (
        NAME,
        ID,
        PICTURE
    )
    VALUES (
        '{pokemon_name}',
        {pokemon_id},
        '{pokemon_sprite}'
    )
    """
    cur.execute(pokemon_query)
    con.commit()


def check_for_and_add_to_move_table(cur, con, pokemon_moves):
    """check for move in database and add if not there
    """
    pokemon_query = f"""
    INSERT OR IGNORE INTO MOVE 
    VALUES (
        ?,
        ?
    )
    """
    cur.executemany(pokemon_query, pokemon_moves)
    con.commit()


def check_for_and_add_to_type_table(cur, con, pokemon_type):
    """check for type in database and add if not there
    """
    pokemon_query = f"""
    INSERT OR IGNORE INTO TYPE
    VALUES (
        ?,
        ?
    )
    """
    cur.executemany(pokemon_query, pokemon_type)
    con.commit()


def add_to_pokemon_move_table(cur, con, name_and_move):
    """combine pokemon name and move into one table
    """
    pokemon_query = f"""
    INSERT INTO POKEMON_MOVE
    VALUES (
        ?,
        ?
    )
    """
    cur.executemany(pokemon_query, name_and_move)
    con.commit()


def add_to_pokemon_type_table(cur, con, name_and_type):
    """combine pokemon name and type into one table
    """
    pokemon_query = f"""
    INSERT INTO POKEMON_TYPE
    VALUES (
        ?,
        ?
    )
    """
    cur.executemany(pokemon_query, name_and_type)
    con.commit()
    print(name_and_type)


def get_pokemon_info(pokemon_response):
    """sort through json results and returns variables
    """
    name = pokemon_response['name']
    pokemon_id = pokemon_response['id']
    sprite = pokemon_response['sprites']['other']['official-artwork']['front_default']

    types = []
    for type_dict in pokemon_response['types']:
        type_url = type_dict["type"]["url"]
        split_type_url = type_url.split("/")
        types.append((type_dict['type']['name'], split_type_url[-2]))

    moves = []
    for move_dict in pokemon_response['moves']:
        move_url = move_dict["move"]["url"]
        split_url = move_url.split("/")
        moves.append((move_dict["move"]["name"], split_url[-2]))

    name_and_move = []
    for move_dict in pokemon_response['moves']:
        name_and_move.append((name, move_dict["move"]["name"]))

    name_and_type = []
    for type_dict in pokemon_response['types']:
        name_and_type.append((name, type_dict['type']['name']))

    return name, pokemon_id, sprite, moves, types, name_and_move, name_and_type


def test_database(cur, pokemon_name):
    """print results from database for testing
    """
    print("\nPOKEMON TABLE: ")
    poke_main_query = f"""
    SELECT * FROM POKEMON
    WHERE NAME = '{pokemon_name}'
    """
    cur.execute(poke_main_query)
    pokemon_result = cur.fetchall()
    poke_list = []
    for row in pokemon_result:
        poke_list.append(row)
    name = poke_list[0][0]
    id = poke_list[0][1]
    image = poke_list[0][2]
    print(f"NAME: {name}\nID: {id}\nIMAGE: {image}")

    # print("\nTYPE TABLE: ")
    # cur.execute("SELECT * FROM TYPE")
    # type_result = cur.fetchall()
    # for row in type_result:
    #     print(row)

    # print("\nMOVE TABLE: ")
    # cur.execute("SELECT * FROM MOVE")
    # move_result = cur.fetchall()
    # for row in move_result:
    #     print(row)

    print("\nPOKEMON_TYPE TABLE: ")
    poke_type_query = f"""
    SELECT * FROM POKEMON_TYPE
    WHERE POKEMON_NAME = '{pokemon_name}'
    """
    cur.execute(poke_type_query)
    type_result = cur.fetchall()
    for row in type_result:
        print(row[1])

    print("\nPOKEMON_MOVE TABLE: ")
    poke_move_query = f"""
    SELECT * FROM POKEMON_MOVE
    WHERE POKEMON_NAME = '{pokemon_name}'
    """
    cur.execute(poke_move_query)
    move_result = cur.fetchall()
    for row in move_result:
        print(row[1])


def main():
    """Contains the main logical flow of the program.
    """
    # connection to pokedex.db and cursor object
    base_url = 'https://pokeapi.co/api/v2/'
    pokemon = input("Enter Pokemon: ").lower()
    con = sqlite3.connect('pokedex.db')
    cur = con.cursor()

    # drop_tables(cur, con)
    create_tables(cur)

    # variables
    pokemon_response = get_pokemon_api_data(base_url, pokemon)
    pokemon_name, pokemon_id, pokemon_sprite, pokemon_moves, pokemon_type, name_and_move, name_and_type = get_pokemon_info(
        pokemon_response)
    # running functions
    check_for_and_add_to_pokemon_table(
        cur, con, pokemon_name, pokemon_id, pokemon_sprite)
    check_for_and_add_to_move_table(cur, con, pokemon_moves)
    check_for_and_add_to_type_table(cur, con, pokemon_type)
    add_to_pokemon_move_table(cur, con, name_and_move)
    add_to_pokemon_type_table(cur, con, name_and_type)

    # print
    test_database(cur, pokemon_name)
    # print(f"\nName: {pokemon_name}\nID: {pokemon_id}\nType: {pokemon_type}\nSprite: {pokemon_sprite}\nMoves: {pokemon_moves}\n")


if __name__ == "__main__":
    main()
