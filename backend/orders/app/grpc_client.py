import grpc
from app.proto import products_pb2, products_pb2_grpc

def get_product_by_id(product_id: int):
    channel = grpc.insecure_channel("products:50051")
    stub = products_pb2_grpc.ProductServiceStub(channel)
    request = products_pb2.ProductRequest(id=product_id)
    response = stub.GetProductById(request)
    return {
        "id": response.id,
        "name": response.name,
        "description": response.description,
        "cost": response.cost,
        "status": response.status,
        "image_url": response.image_url,
        "attributes": response.attributes,
    }
