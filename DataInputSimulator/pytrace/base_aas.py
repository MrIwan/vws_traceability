from basyx.aas import model

from .global_variables import *

from .helper import *

class BaseAAS():

    def __init__(self) -> None:
        self.aas: model.AssetAdministrationShell

    def init_aas(self, aas_id: str) -> model.AssetAdministrationShell:
        aas_dicts = get_all_shells()
        for aas_dict in aas_dicts:
            if aas_dict['id'] == aas_id:
                aas = json_to_aas(aas_dict)
                return aas
        return None
    
    def get_aas(self) -> model.AssetAdministrationShell:
        return self.aas

    def post(self):
        post_aas(self.aas)
    
    def post_sm(sm: model.Submodel) -> bool:
        pass
    
    def get_sm(self, sm_name: str) -> model.Submodel:
        for sm_ref in self.aas.submodel:
            sm = get_sm(sm_ref.get_identifier())
            if sm.id_short == sm_name:
                return sm
        print(f'The Submodell {sm_name} is not present in the aas {self.aas.id_short}')
        return None
    

    def add_sm_el_to_sm(
            self,
            sm_name: str,
            el: model.Property):
        sm = self.get_sm(sm_name)
        existing_el = next((e for e in sm.submodel_element if e.id_short == el.id_short), None)
        if existing_el:
            existing_el.value = el.value  # Aktualisiere den Wert des existierenden Elements
        else:
            sm.submodel_element.add(el)  # Füge das neue Element hinzu
        post_sm(sm, True)


    
    def add_sm(
            self,
            id_: str,
            id_short: str
    ):
        sm = model.Submodel(
            id_ = id_,
            id_short=id_short
        )

        self.aas.submodel.add(model.ModelReference.from_referable(sm))
        post_sm(sm)
