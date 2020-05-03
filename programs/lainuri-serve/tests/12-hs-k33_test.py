#!/usr/bin/python3

import context

import lainuri.hs_k33


def test_format_css_rules_from_config(subtests):
  printer = None
  rtts = None

  with subtests.test("Given a HS-K33 thermal printer"):
    printer = lainuri.hs_k33.get_printer()
    assert printer

  with subtests.test("When the printer real-time transmission status is requested"):
    rtts = printer.real_time_transmission_status(printer_status=True, send_offline_status=True, transmission_error_status=True, transmission_paper_sensor_status=True)
    assert rtts

  with subtests.test("Then the status response looks reasonable"):
    assert rtts.paper_adequate == True or rtts.paper_adequate == False
    assert rtts.paper_ending == True or rtts.paper_ending == False
    assert rtts.paper_out == True or rtts.paper_out == False
    assert rtts.print_head_voltage_and_temperature_over_range == True or rtts.print_head_voltage_and_temperature_over_range == False
    assert rtts.push_feed_button == True or rtts.push_feed_button == False
    assert rtts.unrecoverable_error == True or rtts.unrecoverable_error == False
