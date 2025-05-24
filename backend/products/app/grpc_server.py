import grpc
from concurrent import futures
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app import models
from app.proto import products_pb2, products_pb2_grpc


class ProductService(products_pb2_grpc.ProductServiceServicer):
    def GetProductById(self, request, context):
        db: Session = SessionLocal()
        product = db.query(models.Product).filter(models.Product.id == request.id).first()
        if not product:
            context.abort(grpc.StatusCode.NOT_FOUND, "Product not found")
        return products_pb2.ProductResponse(
            id=product.id,
            name=product.name,
            description=product.description or "",
            cost=float(product.cost),
            status=product.status,
            image_url=product.image_url or "",
            attributes=str(product.attributes or "{}")
        )

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    products_pb2_grpc.add_ProductServiceServicer_to_server(ProductService(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print("gRPC server started on port 50051")
    server.wait_for_termination()
