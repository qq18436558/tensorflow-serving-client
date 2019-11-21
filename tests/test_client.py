import numpy as np

from tensorflow_serving_client import TensorflowServingClient
from keras_model_specs import ModelSpec


MODEL_SERVING_PORTS = {
    'mobilenet_v1': 9001,
    'inception_v3': 9002,
    'xception': 9003
}


def query_model(model_spec_name):
    model_spec = ModelSpec.get(model_spec_name)
    client = TensorflowServingClient('localhost', MODEL_SERVING_PORTS[model_spec_name])
    image = model_spec.load_image('tests/fixtures/files/cat.jpg')
    return client.make_prediction(image, 'image')


def assert_predictions(response, expected_top_5, imagenet_dictionary):
    assert 'class_probabilities' in response
    assert len(response['class_probabilities']) == 1
    assert len(response['class_probabilities'][0]) == 1000
    predictions = response['class_probabilities'][0]
    predictions = list(zip(imagenet_dictionary, predictions))
    predictions = sorted(predictions, reverse=True, key=lambda kv: kv[1])[:5]
    predictions = [(label, float(score)) for label, score in predictions]
    print(predictions)
    classes = [name for name, _ in predictions]
    expected_classes = [name for name, _ in expected_top_5]
    assert classes == expected_classes
    scores = [score for _, score in predictions]
    expected_scores = [score for _, score in expected_top_5]
    np.testing.assert_array_almost_equal(np.array(scores), np.array(expected_scores))


def test_mobilenet_v1(imagenet_dictionary):
    response = query_model('mobilenet_v1')
    assert_predictions(response, [
        ('tiger cat', 0.334694504737854),
        ('Egyptian cat', 0.2851393222808838),
        ('tabby, tabby cat', 0.15471667051315308),
        ('kit fox, Vulpes macrotis', 0.03160465136170387),
        ('lynx, catamount', 0.030886519700288773)
    ], imagenet_dictionary)


def test_inception_v3(imagenet_dictionary):
    response = query_model('inception_v3')
    assert_predictions(response, [
        ('tiger cat', 0.4716886878013611),
        ('Egyptian cat', 0.127954363822937),
        ('Pembroke, Pembroke Welsh corgi', 0.07338221371173859),
        ('tabby, tabby cat', 0.052391838282346725),
        ('Cardigan, Cardigan Welsh corgi', 0.008323794230818748)
    ], imagenet_dictionary)


def test_xception(imagenet_dictionary):
    response = query_model('xception')
    assert_predictions(response, [
        ('red fox, Vulpes vulpes', 0.10058529675006866),
        ('weasel', 0.09152575582265854),
        ('Pembroke, Pembroke Welsh corgi', 0.07581676542758942),
        ('tiger cat', 0.0746716633439064),
        ('kit fox, Vulpes macrotis', 0.06751589477062225)
    ], imagenet_dictionary)
