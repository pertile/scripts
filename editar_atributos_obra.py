
import geopandas as gpd
import fiona
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.key_binding import KeyBindings

# Ruta del archivo geopackage
GPKG_PATH = r"C:\Users\fpertile\OneDrive - FDN\Planos y mapas\highway Resistencia new.gpkg"

# Leer el archivo especificando la capa correcta
print("Cargando datos...")
layer_names = fiona.listlayers(GPKG_PATH)
print("Capas encontradas:", layer_names)
layer = None
for lname in layer_names:
    if lname.strip().lower() == "highway resistencia":
        layer = lname
        break
if not layer:
    layer = layer_names[0]
    print(f"No se encontró la capa 'highway Resistencia', usando la primera: {layer}")
else:
    print(f"Usando capa: {layer}")
gdf = gpd.read_file(GPKG_PATH, layer=layer)

# Obtener lista de obras únicas
obras = sorted(set(gdf['Obra'].dropna().unique()))

# Autocompletado para elegir obra
obras_completer = WordCompleter(obras, ignore_case=True, match_middle=True, sentence=True)
bindings = KeyBindings()

@bindings.add('tab')
@bindings.add('enter')
def _(event):
    buffer = event.app.current_buffer
    document = buffer.document
    completions = list(buffer.completer.get_completions(document, event.app))
    if completions:
        buffer.delete_before_cursor(len(document.text_before_cursor))
        buffer.insert_text(completions[0].text)
        event.app.exit(result=completions[0].text)


# Bucle para permitir cambiar de obra antes de editar y grabar
while True:
    obra_seleccionada = prompt("Ingrese el nombre de la obra: ", completer=obras_completer, key_bindings=bindings)
    candidatas = [o for o in obras if obra_seleccionada.lower() in o.lower()]
    print("Obras candidatas:")
    for idx, o in enumerate(candidatas):
        print(f"{idx+1}. {o}")
    if not candidatas:
        print("No se encontraron obras candidatas.")
        continue
    if len(candidatas) == 1:
        idx = 0
    else:
        idx = int(input("Seleccione el número de la obra a editar: ")) - 1
    obra_final = candidatas[idx]
    mask = gdf['Obra'] == obra_final
    features = gdf[mask]
    print(f"Se editarán {len(features)} features de la obra '{obra_final}'")
    print("Valores actuales:")
    print(features[['title','name','municipality', 'length', 'link_progress', 'link_finished']])

    # Pedir nuevos valores
    new_muni = input("Nuevo valor para 'municipality' (dejar vacío para no cambiar): ")
    new_progress_link = input("Nuevo valor para 'link_progress' (dejar vacío para no cambiar): ")
    new_finished_link = input("Nuevo valor para 'link_finished' (dejar vacío para no cambiar): ")
    new_title = input("Nuevo valor para 'title' (dejar vacío para no cambiar): ")
    new_length = input("Nuevo valor para 'length' (dejar vacío para no cambiar): ")

    # Editar atributos
    if new_muni:
        gdf.loc[mask, 'municipality'] = new_muni
    if new_progress_link:
        gdf.loc[mask, 'link_progress'] = new_progress_link
    if new_finished_link:
        gdf.loc[mask, 'link_finished'] = new_finished_link
    if new_title:
        gdf.loc[mask, 'title'] = new_title
    if new_length:
        # Intentar convertir a float si es posible
        try:
            gdf.loc[mask, 'length'] = float(new_length)
        except ValueError:
            print("Advertencia: El valor de 'length' no es numérico. Se guarda como texto.")
            gdf.loc[mask, 'length'] = new_length
    
    resp = input("¿Desea editar otra obra? (s/n): ").strip().lower()
    if resp == 'n':
        break
    

# Guardar archivo
backup_path = GPKG_PATH.replace('.gpkg', '_backup.gpkg')
gdf.to_file(GPKG_PATH, driver="GPKG", layer=layer)
print(f"Archivo guardado en la capa '{layer}'. Backup sugerido: {backup_path}")
