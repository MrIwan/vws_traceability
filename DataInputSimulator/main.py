from pytrace import *

from typing import List

from basyx.aas import model

from datetime import datetime, timedelta

def choose_product_type_input_dialog():
    print("Verfügbare Produkttypen:")
    available_product_types = get_product_types()
    for i, pt in enumerate(available_product_types):
        print(f"{i}. {pt['idShort']}")
    
    while True:
        try:
            index = int(input("Wählen Sie eine Komponente (oder -1 zum Beenden): "))
            if index == -1:
                return None
            
            if 0 <= index < len(available_product_types):
                return available_product_types[index]
            else:
                print("Ungültiger Index. Bitte wählen Sie einen gültigen Index.")
        except ValueError:
            print("Ungültige Eingabe. Bitte geben Sie eine Zahl ein.")

def place_order():
    # Material erfassen
    print('Whitch Material you want to produce?')
    materials = get_product_types()
    for i, aas in enumerate(materials):
        print(f'{i}. {aas}')
    print('\n')


    index_mat = int(input('Chose Material'))
    chosen_material = materials[index_mat]

    # Order erstellen und Inputs abfragen
    materail_id = str(chosen_material['id']).split('/')[-1]
    order = ProductionOrder(
        material_id=materail_id,
        order_id=create_chargen_id(),
        prod_type_ref=chosen_material['id']
    )
    
    # Batches erstellen
    batch = Batch(
        material_id=materail_id,
        batch_id=create_chargen_id(),
    )

    # Lots erstellen
    lot = Lot(
        material_id=materail_id,
        lot_id=create_chargen_id(),
    )

    # Material erstellen
    product = Product(
        sertail_number=create_chargen_id(),
        prod_type_dict=chosen_material
    )

    product.add_sm_nameplate()

    lot.add_run()
    lot.run_add_step()
    lot.step_add_prod_material(product.get_aas().id)

    batch.add_lot_ref(lot.get_aas().id)

    order.add_batch_ref(batch.get_aas().id)


def add_product_type():
    # Eingabe für Produkt-ID und Name
    product_id = input("Geben Sie die Produkt-ID ein: ")
    product_name = input("Geben Sie den Produktnamen ein: ")

    # Erstellen eines neuen ProductType-Objekts
    product_type = ProductType(product_id, product_name)
    product_type.add_sm_nameplate()

    steps = 0
    while True:

        add_another = input("Möchten Sie einen Prozess Schritt hinzufügen? (Enter = ja/q = nein): ")
        if add_another.lower() == 'q':
            break
        steps += 1
        
        print("\nProzessschritt hinzufügen:")
        process_id = int(input("Prozess-ID: "))
        process_name = input("Prozessname: ")
        process_description = input("Prozessbeschreibung: ")
        planned_process_time = float(input("Geplante Prozesszeit: "))

        product_type.add_bob_step(process_id, process_name, process_description, planned_process_time)

        # 3. Hinzufügen von Komponenten
        while True:
            chosen_product_type = choose_product_type_input_dialog()

            if chosen_product_type:
                nominal_percentage_share = float(input("Geben Sie den nominalen Prozentanteil ein: "))
                product_type.add_product_parameters(nominal_percentage_share, chosen_product_type['id'])
            else:
                break
            

        # 5. Hinzufügen von Prozessparametern
        while True:
            param_name = input("\nGeben Sie den Namen des Prozessparameters ein (oder Enter zum Beenden): ")
            if param_name == "":
                break
            param_value = input("Geben Sie den Wert des Prozessparameters ein: ")
            param_type = input("Geben Sie den Datentyp des Parameters ein (String/Int/Float): ")

            if param_type.lower() == "string":
                value_type = model.datatypes.String
            elif param_type.lower() == "int":
                value_type = model.datatypes.Int
                param_value = int(param_value)
            elif param_type.lower() == "float":
                value_type = model.datatypes.Float
                param_value = float(param_value)
            else:
                print("Ungültiger Datentyp. Parameter wird als String gespeichert.")
                value_type = model.datatypes.String

            property = model.Property(
                id_short=param_name,
                value_type=value_type,
                value=param_value
            )
            product_type.add_process_parameter(property)
        

    product_type.post()
    return

from basyx.aas import model

def add_product():
    # 1. Wähle welchen Product Typ
    chosen_product_type = add_product_input_dialog()
    if not chosen_product_type:
        return None

    # Erstelle ein neues Produkt
    new_product = Product(
        sertail_number=create_chargen_id(),
        prod_type_dict=chosen_product_type
    )

    # 3. Möglichkeit das Nameplate hinzuzufügen
    add_nameplate = input("Möchten Sie ein Nameplate hinzufügen? (j/n): ").lower() == 'j'
    if add_nameplate:
        new_product.add_sm_nameplate()

    # 4. Möglichkeit Carbon Footprint hinzuzufügen
    add_carbon_footprint = input("Möchten Sie einen Carbon Footprint hinzufügen? (j/n): ").lower() == 'j'
    if add_carbon_footprint:
        while True:
            try:
                ausstoss = float(input("Geben Sie den CO2-Äquivalent-Ausstoß ein: "))
                new_product.add_sm_carbon_footprint(ausstoss)
                break
            except ValueError:
                print("Ungültige Eingabe. Bitte geben Sie eine Zahl ein.")

    new_product.get_sm('temp')
    # new_product.post()

def add_product_input_dialog():
    print("Verfügbare Produkttypen:")
    available_product_types = get_product_types()
    for i, pt in enumerate(available_product_types):
        print(f"{i}. {pt['idShort']}")
    
    while True:
        try:
            index = int(input("Wählen Sie eine Komponente (oder -1 zum Beenden): "))
            if index == -1:
                return None
            
            if 0 <= index < len(available_product_types):
                return available_product_types[index]
            else:
                print("Ungültiger Index. Bitte wählen Sie einen gültigen Index.")
        except ValueError:
            print("Ungültige Eingabe. Bitte geben Sie eine Zahl ein.")

def simulate_all():
    print('Data Input Simulator startet.')
    input('Press Enter to add Materials for Silicone')

    # Hinzufügen von Material das benutzt werden soll
    comp1 = Product(
        create_chargen_id(),
        prod_type_dict={'id': 'http://example.com/mat/1/aas', 'idShort': 'SiliconeBaseType'}
    )

    comp2 = Product(
        create_chargen_id(),
        prod_type_dict={'id': 'http://example.com/mat/1/aas', 'idShort': 'CatalystType'}
    )

    comp3 = Product(
        create_chargen_id(),
        prod_type_dict={'id': 'http://example.com/mat/1/aas', 'idShort': 'ColorPasteType'}
    )

    print('Components Added')
    input('Press Enter to produce Silicone')

    # Produktion von Silikon

    ## Befüllen
    lot = Lot(
        '1',
        create_chargen_id()
    )
    lot.add_run()
    lot.run_add_step()
    lot.step_add_bom_material(comp1.get_aas().id)
    lot.step_add_bom_material(comp2.get_aas().id)
    lot.step_add_bom_material(comp3.get_aas().id)
    

    ## Kneten
    lot.run_add_step()
    lot.step_add_process_parameter(parameter_name='Speed',
                                   nominal_value= 3500.0, 
                                   actual_value= 1503.0)
    
#     # Beispielaufruf
#     lot.step_add_time_series(
#         parameter_name="EnvironmentalData",
#         time_series_name="EnvironmentalTimeSeries",
#         num_points=5,  # Generiert 50 Datenpunkte
# )


    # Aktueller Zeitstempel für StartTime
    start_time = datetime.now()

    # EndTime 10 Sekunden in der Zukunft
    end_time = start_time + timedelta(seconds=10)

    lot.step_add_property(prop=model.Property(
        id_short='StartTime',
        value_type=model.datatypes.DateTime,
        value=start_time
    ))

    lot.step_add_property(prop=model.Property(
        id_short='EndTime',
        value_type=model.datatypes.DateTime,
        value=end_time
    ))


    ## Abfüllen
    lot.run_add_step()

    prod = Product(
        create_chargen_id(),
        prod_type_dict={'id': 'http://example.com/mat/1/aas', 'idShort': 'SilikonType'}
    )

    lot.step_add_prod_material(prod.get_aas().id)

    # Produce Cable
    print('Silikone produced')
    input('Press Enter to produce a Cable')
    
    comp4 = Product(
        create_chargen_id(),
        prod_type_dict={'id': 'http://example.com/mat/1/aas', 'idShort': 'CopperType'}
    )

    prod2 = Product(
        create_chargen_id(),
        prod_type_dict={'id': 'http://example.com/mat/2/aas', 'idShort': 'CableType'}
    )

    lot = Lot(
        '2',
        create_chargen_id()
    )
    lot.add_run()
    lot.run_add_step()
    lot.step_add_bom_material(comp4.get_aas().id, 10.3, 11.0)
    lot.step_add_bom_material(prod.get_aas().id, 2.1, 2.0)
    lot.step_add_prod_material(prod2.get_aas().id)

    print('Simulator is finished!')


if __name__ == "__main__":
    # place_order()
    # add_product_type()
    # add_product()
    # print(get_product_types())

    
    simulate_all() # CQ1 CQ2

    