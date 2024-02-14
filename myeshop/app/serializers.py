from rest_framework import serializers
from .models import Product

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id' , 'title' , 'selling_price' ,  'discounted_price' , 'brand' , 'category' , 'product_image']
