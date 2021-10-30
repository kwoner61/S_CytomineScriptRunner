from cytomine import Cytomine
from cytomine.utilities.descriptor_reader import read_descriptor

host = "http://localhost-core"
public_key = "69cb5962-435c-40c6-8ba6-b6eaf37e2137"
private_key = "451eaf8f-d23b-4dd8-9524-c58d5423cc3b"

with Cytomine(host, public_key, private_key) as c:
    read_descriptor("descriptor.json")
