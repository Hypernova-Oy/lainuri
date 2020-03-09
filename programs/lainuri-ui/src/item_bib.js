'use strict'

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
  status_check_in = Status.NOT_SET;
  states_check_in = {};
  status_check_out = Status.NOT_SET;
  states_check_out = {};
  status_set_tag_alarm = Status.NOT_SET;
  states_set_tag_alarm = {};

  constructor(item_barcode_or_tag, author, title, edition, book_cover_url) {
    if (typeof(item_barcode_or_tag) === String) {
      this.item_barcode = item_barcode_or_tag
      this.author = author
      this.title = title
      this.edition = edition
      this.book_cover_url = book_cover_url
    }
    else {
      let tag = item_barcode_or_tag
      this.item_barcode = tag.item_barcode
      this.author = tag.author
      this.title = tag.title
      this.edition = tag.edition
      this.book_cover_url = tag.book_cover_url
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
    this.status_check_in = Status.NOT_SET;
    this.states_check_in = {};
    this.status_check_out = Status.NOT_SET;
    this.states_check_out = {};
    this.status_set_tag_alarm = Status.NOT_SET;
    this.states_set_tag_alarm = {};
  }

  get_status_summary(force = false) {
    if (!(force) && this.status) return this.status;
    else if (this.status_check_in === Status.PENDING || this.status_set_tag_alarm === Status.PENDING) this.status = Status.PENDING;
    else if (this.status_check_in === Status.ERROR   || this.status_set_tag_alarm === Status.ERROR)   this.status = Status.ERROR;
    else if (this.status_check_in === Status.SUCCESS && this.status_set_tag_alarm === Status.SUCCESS) this.status = Status.SUCCESS;
    else if (this.status_check_in === Status.NOT_SET || this.status_set_tag_alarm === Status.NOT_SET) this.status = Status.NOT_SET;
    else this.status = Status.ERROR
    return this.status
  }
}
