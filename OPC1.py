from flask import Flask, render_template_string
from opcua import Client

app = Flask(__name__)

# OPC UA server endpoint
OPC_URL = "opc.tcp://127.0.0.1:4840"

@app.route("/")
def show_tags():
    client = Client(OPC_URL)
    tags = []

    try:
        client.connect()
        objects = client.get_objects_node()

        # Recursive browse and read values
        def browse_node(node):
            for child in node.get_children():
                try:
                    name = child.get_browse_name().Name
                    nodeid = child.nodeid.to_string()
                    value = None
                    try:
                        value = child.get_value()
                    except:
                        value = "N/A"
                    tags.append({"name": name, "nodeid": nodeid, "value": value})
                except:
                    pass
                browse_node(child)

        browse_node(objects)

    finally:
        client.disconnect()

    # HTML template for table
    html = """
    <!doctype html>
    <html>
      <head>
        <title>OPC UA Tags</title>
        <style>
          table { border-collapse: collapse; width: 80%; margin: 20px auto; }
          th, td { border: 1px solid #ccc; padding: 8px; text-align: left; }
          th { background-color: #f2f2f2; }
        </style>
      </head>
      <body>
        <h2 style="text-align:center;">OPC UA Tags from Server</h2>
        <table>
          <tr><th>Tag Name</th><th>NodeId</th><th>Value</th></tr>
          {% for tag in tags %}
          <tr>
            <td>{{ tag.name }}</td>
            <td>{{ tag.nodeid }}</td>
            <td>{{ tag.value }}</td>
          </tr>
          {% endfor %}
        </table>
      </body>
    </html>
    """
    return render_template_string(html, tags=tags)

if __name__ == "__main__":
    app.run(debug=True)
