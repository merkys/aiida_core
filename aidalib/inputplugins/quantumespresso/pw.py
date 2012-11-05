from aidalib.inputplugins.exceptions import InputValidationError
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
import json
import os

# List of namelists (uppercase) that are allowed to be found in the
# input_data, in the correct order
_compulsory_namelists = ['CONTROL', 'SYSTEM', 'ELECTRONS']

# List of cards (uppercase) that are allowed to be found in the
# input_data. 'atomic_species', 'atomic_positions' not allowed since they
# are automatically generated by the plugin
_allowed_cards = ['K_POINTS', 'CONSTRAINTS', 'OCCUPATIONS']

# This is used to set the if_pos value in the ATOMIC_POSITIONS card
_further_allowed = ['BLOCKED_COORDS']

_calc_types_noionscells = ['scf','nscf','bands']
_calc_types_onlyions = ['relax', 'md']
_calc_types_bothionscells = ['vc-relax', 'vc-md']

def get_suggestion(provided_string,allowed_strings):
    try:
        import difflib
        
        similar_kws = difflib.get_close_matches(provided_string,
                                                allowed_strings)
        if len(similar_kws)==1:
            return "(Maybe you wanted to specify {0}?)".format(similar_kws[0])
        elif len(similar_kws)>1:
            return "(Maybe you wanted to specify one of these: {0}?)".format(string.join(similar_kws,', '))
        else:
            return "(No similar keywords found...)"
    except ImportError:
        return ""

def conv_to_fortran(val):
    """
    val: the value to be read and converted to a Fortran-friendly string.
    """   
    # Note that bool should come before integer, because a boolean matches also
    # isinstance(...,int)
    if (isinstance(val,bool)):
        if val:
            val_str='.true.'
        else:
            val_str='.false.'
    elif (isinstance(val,int)): 
        val_str = "%d" % val
    elif (isinstance(val,float)):
        val_str = ("%18.10e" % val).replace('e','d')
    elif (isinstance(val,basestring)):
        val_str="'%s'" % val
    else:
        raise ValueError

    return val_str

def get_input_data_text(key,val):
    # I don't try to do iterator=iter(val) and catch TypeError because
    # it would also match strings
    if hasattr(val,'__iter__'):
        # a list/array/tuple of values
        list_of_strings = [
            "  {0}({2}) = {1}\n".format(key, conv_to_fortran(itemval),
                                        idx+1)
            for idx, itemval in enumerate(val)]
        return "".join(list_of_strings)
    else:
        # single value
        return "  {0} = {1}\n".format(key, conv_to_fortran(val))

def create_calc_input(calc, infile_dir):
    """
    Create the necessary input files in infile_dir for calculation calc.

    Note: for the moment, it requires that flags are provided lowercase,
        while namelists/cards are provided uppercase.
    
    Args:
        calc: the calculation object for which we want to create the 
            input file structure.
        infile_dir: the directory where we want to create the files.

    Returns:
        a dictionary with the following keys:
            retrieve_output: a list of files, directories or patterns to be
                retrieved from the cluster scratch dir and copied in the
                permanent aida repository.
            cmdline_params: a (possibly empty) string with the command line
                parameters to pass to the code.
            stdin: a string with the file name to be used as standard input,
                or None if no stdin redirection is required. 
                Note: if you want to pass a string, create a file with the 
                string and use that file as stdin.
            stdout: a string with the file name to which the standard output
                should be redirected, or None if no stdout redirection is
                required. 
            stderrt: a string with the file name to which the standard error
                should be redirected, or None if no stderr redirection is
                required. 
            preexec: a (possibly empty) string containing commands that may be
                required to be run before the code executes.
            postexec: a (possibly empty) string containing commands that may be
                required to be run after the code has executed.

    TODO: this function should equally work if called from the API client or
        from within django. To check/implement! May require some work

    TODO: decide whether to return a namedtuple instead of a dict
        (see http://docs.python.org/2/library/collections.html#namedtuple-factory-function-for-tuples-with-named-fields )
    """
    retdict = {}
    retdict['retrieve_output'] = ['aida.out', 'out/data-file.xml'] 
    retdict['cmdline_params'] = "" # possibly -npool and similar
    retdict['stdin'] = 'aida.in'
    retdict['stdout'] = 'aida.out'
    retdict['stderr'] = None
    retdict['preexec'] = ""
    retdict['postexec'] = ""

    input_filename = os.path.join(infile_dir,retdict['stdin'])

    try: 
        input_structure = calc.inpstruc.get()
    except (ObjectDoesNotExist, MultipleObjectsReturned):
        raise InputValidationError('One and only one input structure must be'
                                   'attached to a QE pw.x calculation')

    try:
        input_data = json.loads(calc.data)['input_data']
    except (ValueError, KeyError):
        input_data = {}
        
    try:
        control_nl = input_data['CONTROL']
        calculation_type = control_nl['calculation']
    except KeyError as e:
        raise InputValidationError("No 'calculation' in CONTROL namelist.")
            
    if calculation_type in _calc_types_noionscells:
        namelists_toprint = _compulsory_namelists
    elif calculation_type in _calc_types_bothionscells:
        namelists_toprint = _compulsory_namelists + ['IONS', 'CELL']
    elif calculation_type in _calc_types_onlyions:
        namelists_toprint = _compulsory_namelists + ['IONS']
    else:
        sugg_string = get_suggestion(calculation_type,
                                     _calc_types_noionscells + 
                                     _calc_types_onlyions + 
                                     _calc_types_bothionscells)
        raise InputValidationError("Unknown 'calculation' value in "
                                   "CONTROL namelist {}".format(sugg_string))

    with open(input_filename,'w') as infile:
        for namelist in namelists_toprint:
            infile.write("&{0}\n".format(namelist.upper()))           
            # namelist content
            try:
                for k, v in sorted(input_data[namelist].iteritems()):
                    infile.write(get_input_data_text(k,v))
            except KeyError:
                # namelist not explicitly mentioned in input_data:
                # leave it empty
                pass
            infile.write("/\n")
            
 

    return retdict

