export function find_tag_by_key (tags, key, value) {
  for (let i in tags) {
    let tag = tags[i]
    if (tag[key] === value) return tag;
  }
  return null
}

export function find_tag_by_key_from_lists (tags_lists, key, value) {
  for (let j in tags_lists) {
    let tag = find_tag_by_key(tags_lists[j], key, value)
    if (tag) return tag;
  }
  return null
}

export function splice_bib_item_from_array (array_to_splice, key, value) {
  for (let i=0 ; i<array_to_splice.length ; i++) {
    if (array_to_splice[i][key] === value) {
      console.log(array_to_splice, key, value)
      array_to_splice.splice(i--, 1);
    }
  }
}

/**
 * Pushes the given element to the first array in the list if the given element with optional key/value was not found in any of the given arrays.
 * @param {Array} arrays
 * @param {Object} element
 * @param {String} key
 * @param {*} value
 * @returns {True} if pushing happened
 * @returns {False} if element was present in one of the arrays
 */
export function push_if_not_exists(arrays, element, key, value) {
  let found = false
  arrays.forEach(array => {
    if (key) {
      for (let i=0 ; i<array.length ; i++) {
        if (array[i][key] === value) {
          found = true
          return false
        }
      }
    }
    else {
      for (let i=0 ; i<array.length ; i++) {
        if (array[i] === element) {
          found = true
          return false
        }
      }
    }
  });
  if (!found) {
    return arrays[0].push(element)
  }
  return false
}

export function in_list(lookup, list) {
  list.forEach((val) => {
    console.log(val, lookup)
    if (val === lookup) {
      return true
    }
  });
  return false
}