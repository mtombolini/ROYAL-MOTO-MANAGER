from flask import Blueprint, request, jsonify

webhook_blueprint = Blueprint('webhook', __name__)

@webhook_blueprint.route('/webhook_notifications', methods=['POST', 'PUT'])
def webhook_notifications():
    # Verifica si la solicitud tiene un payload JSON
    if request.is_json:
        # Obtén el contenido del JSON
        data = request.get_json()
        
        # Aquí puedes procesar los datos según necesites. Por ejemplo, imprimirlos en la consola o guardarlos en una base de datos.
        print("Datos recibidos del webhook:", data)

        # También puedes diferenciar el procesamiento según el tipo de método HTTP utilizado (POST o PUT)
        if request.method == 'POST':
            print("Manejando una solicitud POST")
            # Procesa los datos específicos de POST aquí
        elif request.method == 'PUT':
            print("Manejando una solicitud PUT")
            # Procesa los datos específicos de PUT aquí
        
        # Devuelve una respuesta de éxito.
        return jsonify({'status': 'success', 'message': 'Datos recibidos correctamente'}), 200
    else:
        # Si la solicitud no es JSON o está vacía, devuelve un error.
        return jsonify({'status': 'error', 'message': 'Formato de solicitud incorrecto'}), 400
