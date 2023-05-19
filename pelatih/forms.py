from django import forms
from utils.query import *

class PendaftaranAtlet(forms.Form):
    dropdown = forms.ChoiceField(choices=[])

    def __init__(self, *args, **kwargs):
        super(PendaftaranAtlet, self).__init__(*args, **kwargs)

        query_all_atlet = '''
        SELECT 
            M.nama, A.id
        FROM 
            atlet A 
            INNER JOIN member M ON (A.id = M.id);
        '''
        list_all_atlet = execute_query(query_all_atlet)
        choices = [('$not_complete$','Pilih Atlet')]
        for row in list_all_atlet:
            choices.append((row[1], row[0]))

        self.fields['dropdown'].choices = choices