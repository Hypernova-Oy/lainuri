'use strict'

import {translate_exception} from './exception.js'
import {Status} from './lainuri_events';

/**
 * Container for all things that revolve around an libary Item found via RFID tag or a whose barcode is read
 */

export class ItemBib {
  item_barcode = '';
  tag_type = 'rfid' || 'barcode';

  author = '';
  title = '';
  edition = '';
  book_cover_url = '';

  /** Summary of all other transaction step statuses */
  status = Status.NOT_SET
  states = {}
  status_check_in = Status.NOT_SET;
  states_check_in = {};
  status_check_out = Status.NOT_SET;
  states_check_out = {};
  status_set_tag_alarm = Status.NOT_SET;
  states_set_tag_alarm = {};

  constructor(item_barcode_or_tag, author, title, edition, book_cover_url) {
    if (typeof(item_barcode_or_tag) === String) {
      throw Error(`Passed a String '${item_barcode_or_tag}' instead of a tag-object!`)
    }
    else {
      let tag = item_barcode_or_tag
      this.item_barcode = tag.item_barcode
      this.serial_number = tag.serial_number
      this.author = tag.author
      this.title = tag.title
      this.edition = tag.edition
      this.book_cover_url = tag.book_cover_url
      this.tag_type = tag.tag_type || this.tag_type

      if (tag.status === Status.ERROR) {
        this.status = tag.status;
        this.states = translate_exception(tag.states);
      }
    }
  }

  set_status_check_in(status, states = null) {
    this.status_check_in = status
    if (states) this.states_check_in = states;
    this.get_status_summary(true)
  }

  set_status_check_out(status, states = null) {
    this.status_check_out = status
    if (states) this.states_check_out = states;
    this.get_status_summary(true)
  }

  set_status_set_tag_alarm(status, states = null) {
    this.status_set_tag_alarm = status
    if (states) this.states_set_tag_alarm = states;
    this.get_status_summary(true)
  }

  flush_statuses() {
    this.status = Status.NOT_SET
    this.states = {}
    this.status_check_in = Status.NOT_SET;
    this.states_check_in = {};
    this.status_check_out = Status.NOT_SET;
    this.states_check_out = {};
    this.status_set_tag_alarm = Status.NOT_SET;
    this.states_set_tag_alarm = {};
  }

  get_status_summary(force = false) {
    if (!(force) && this.status) return this.status;

    let check_status;
    if (this.status_check_in !== Status.NOT_SET) check_status = this.status_check_in;
    else if (this.status_check_out !== Status.NOT_SET) check_status = this.status_check_out;

    let set_tag_alarm_status;
    if (this.tag_type === 'barcode') set_tag_alarm_status = Status.SUCCESS
    else set_tag_alarm_status = this.status_set_tag_alarm

    if      (check_status === Status.PENDING || set_tag_alarm_status === Status.PENDING) this.status = Status.PENDING;
    else if (check_status === Status.ERROR   || set_tag_alarm_status === Status.ERROR)   this.status = Status.ERROR;
    else if (check_status === Status.SUCCESS && set_tag_alarm_status === Status.SUCCESS) this.status = Status.SUCCESS;
    else if (check_status === Status.NOT_SET || set_tag_alarm_status === Status.NOT_SET) this.status = Status.NOT_SET;
    else this.status = Status.ERROR

    this.states = translate_exception(this.states_check_in,this.states_check_out,this.states_set_tag_alarm);

    return this.status
  }

  has_exception() {
    if (Object.keys(this.states_check_in).length || Object.keys(this.states_check_out).length || Object.keys(this.set_status_set_tag_alarm).length) {
      return true
    }
    return false
  }
}
