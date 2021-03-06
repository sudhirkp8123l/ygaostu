import tensorflow as tf
import numpy as np
import time, argparse
from PIL import Image
from data import create_image_dataset
from model import create_model

if __name__ == "__main__":
    start = time.time()
    parser = argparse.ArgumentParser()
    parser.add_argument("--batch_size", default=4, type=int)
    parser.add_argument("--validate_path", type=str, default="./data/ssepi")
    parser.add_argument("--save_path", type=str, default="./data/rec_dsepi")
    parser.add_argument("--tensorboard_path", type=str, default="./tensorboard")
    parser.add_argument("--shearlet_system_path", type=str, default="./model/st_127_127_4.mat")
    args = parser.parse_args()

    # setup logging
    tf.logging.set_verbosity(tf.logging.INFO)

    dataset_params = {
        "validate_path": args.validate_path,
        "save_path": args.save_path,
    }

    def validate_fn():
        dataset_eval = create_image_dataset(train=False, params=dataset_params).batch(args.batch_size)
        eval_it = dataset_eval.make_one_shot_iterator()
        return eval_it.get_next()

    estimator = tf.estimator.Estimator(
        model_fn=create_model,
        params={
            "batch_size": args.batch_size,
            "tensorboard_dir": args.tensorboard_path,
            "shearlet_system_path": args.shearlet_system_path,
            "num_output_channels": 3,
            "height": 128,
            "width": 608, 
            "alpha": 2,
            "niter": 30,
            "thmax": 2,
            "thmin": 0.02
        },
        config=tf.estimator.RunConfig(
            model_dir=args.tensorboard_path,
        )
    )

    predictions = estimator.predict(input_fn=validate_fn)

    for i, pred_dict in enumerate(predictions):
        save_name, im_rec = pred_dict["save_name"].decode("utf-8"), pred_dict["image"]
        Image.fromarray(im_rec).save(save_name)
        print("Image saved in", save_name)
        
    print('Required time: {:.3f} s'.format(time.time() - start) )
