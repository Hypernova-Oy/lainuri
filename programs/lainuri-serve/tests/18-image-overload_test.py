#!/usr/bin/python3

import context

import lainuri.config
import lainuri.helpers

import pathlib

def test_image_overloads(subtests):
  with subtests.test("Given the deployed image overloads are flushed"):
    lainuri.config.image_overloads_flush()
    assert lainuri.config.image_overloads_get_images() == []

  with subtests.test("When the 'ui.images'-configuration is handled"):
    lainuri.config.image_overloads_handle()

  with subtests.test("Then the configured images are present"):
    images_found = ' '.join([str(path) for path in lainuri.config.image_overloads_get_images()])
    assert 'Place_to_bin_OK.png' in images_found
    assert 'Place_to_bin_ODD.png' in images_found
