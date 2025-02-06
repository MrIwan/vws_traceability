from basyx.aas import model
from .global_variables import *
from .helper import *
from .base_aas import BaseAAS

class Product(BaseAAS):
    def __init__(self, 
                 sertail_number: str,
                 prod_type_dict: dict,
                 ) -> None:
        
        self.product_id = int(str(prod_type_dict['id']).split("/")[-2])
        self.sertail_number = sertail_number
        self.prod_type_ref = prod_type_dict['id']
        self.material_name = str(prod_type_dict['idShort']).replace('Type', '')

        aas_id = f'{id_url}mat/{self.product_id}/{sertail_number}/aas'

        aas = self.init_aas(aas_id)

        if not aas:
            asset_information = model.AssetInformation(
                asset_kind=model.AssetKind.INSTANCE,
                global_asset_id=f'{id_url}mat/{self.product_id}'
            )

            self.aas = model.AssetAdministrationShell(
                id_ = aas_id,
                id_short=f'{self.material_name}_',
                asset_information = asset_information
            )

            self.add_sm(
                id_ = f'{id_url}mat_{self.product_id}/{self.sertail_number}/sm/nameplate',
                id_short='Nameplate'
            )

            self.add_sm(
                id_ = f'{id_url}mat/{self.product_id}/{self.sertail_number}/sm/carbon_footprint',
                id_short='CarbonFootprint'
            )
            post_aas(self.aas)

        else: 
            self.aas = aas

    def add_sm_nameplate(self):
        self.add_sm_el_to_sm(
            'Nameplate',
            model.Property(
                id_short='Name',
                value_type=model.datatypes.String,
                value=f'{self.material_name}'
            )
        )

        self.add_sm_el_to_sm(
            'Nameplate',
            model.Property(
                id_short='Charge',
                value_type=model.datatypes.String,
                value=f'{self.sertail_number}'
            )
        )

        self.add_sm_el_to_sm(
            'Nameplate',
            model.ReferenceElement(
                id_short='TypeRef',
                value=create_model_reference_from_global_id(self.prod_type_ref)
            )
        )