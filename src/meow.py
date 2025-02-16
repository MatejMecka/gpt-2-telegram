#!/usr/bin/env python3

import fire
import json
import os
import numpy as np
import tensorflow as tf

import model, sample, encoder


import logging
from time import sleep
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram.error import NetworkError, Unauthorized
update_id = None

def interact_model(
    model_name='117M',
    seed=None
    nsamples=1,
    batch_size=1,
    length=None,
    temperature=1,
    top_k=40,
):
    """
    Interactively run the model
    :model_name=117M : String, which model to use
    :seed=None : Integer seed for random number generators, fix seed to reproduce
     results
    :nsamples=1 : Number of samples to return total
    :batch_size=1 : Number of batches (only affects speed/memory).  Must divide nsamples.
    :length=None : Number of tokens in generated text, if None (default), is
     determined by model hyperparameters
    :temperature=1 : Float value controlling randomness in boltzmann
     distribution. Lower temperature results in less random completions. As the
     temperature approaches zero, the model will become deterministic and
     repetitive. Higher temperature results in more random completions.
    :top_k=0 : Integer value controlling diversity. 1 means only 1 word is
     considered for each step (token), resulting in deterministic completions,
     while 40 means 40 words are considered at each step. 0 (default) is a
     special setting meaning no restrictions. 40 generally is a good value.
    """
    if batch_size is None:
        batch_size = 1
    assert nsamples % batch_size == 0

    enc = encoder.get_encoder(model_name)
    hparams = model.default_hparams()
    with open(os.path.join('models', model_name, 'hparams.json')) as f:
        hparams.override_from_dict(json.load(f))

    if length is None:
        length = hparams.n_ctx // 2
    elif length > hparams.n_ctx:
        raise ValueError("Can't get samples longer than window size: %s" % hparams.n_ctx)

    with tf.Session(graph=tf.Graph()) as sess:
        context = tf.placeholder(tf.int32, [batch_size, None])
        np.random.seed(seed)
        tf.set_random_seed(seed)
        output = sample.sample_sequence(
            hparams=hparams, length=length,
            context=context,
            batch_size=batch_size,
            temperature=temperature, top_k=top_k
        )

        saver = tf.train.Saver()
        ckpt = tf.train.latest_checkpoint(os.path.join('models', model_name))
        saver.restore(sess, ckpt)
        print('Loading bot...')
    # Telegram Bot Authorization Token
    # get the frst pending update_id, this is so we can skip over it in case
    # we get an "Unauthorized" exception.
        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        print('LOADED')
        def echo(bot, update):
            print(update.message.text)
            raw_text = update.message.text
            context_tokens = enc.encode(raw_text)
            generated = 0
            for _ in range(nsamples // batch_size):
                out = sess.run(output, feed_dict={
                    context: [context_tokens for _ in range(batch_size)]
                })[:, len(context_tokens):]
                for i in range(batch_size):
                    generated += 1
                    story = enc.decode(out[i])
                    bot.send_message(chat_id=update.message.chat_id, text=story)
                    print(story)

        def runrunrun(bot, update):
            bot.send_message(chat_id=update.message.chat_id, text='Type a message to begin...')
        def error():
            pass
        updater = Updater("BOTKEY")
        dp = updater.dispatcher
        dp.add_error_handler(error)
        dp.add_handler(CommandHandler('start', runrunrun))
        dp.add_handler(MessageHandler(Filters.text, echo))
        updater.start_polling()
        updater.idle()

if __name__ == '__main__':
    fire.Fire(interact_model)

