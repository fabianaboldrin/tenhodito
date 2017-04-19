function getElementFontSize(context = null) {
  return parseFloat(
      getComputedStyle(
          context || document.documentElement
      ).fontSize
  );
}

function convertEm(value, context = null) {
  return value * getElementFontSize(context);
}

function convertRem(value) {
  return convertEm(value);
}

export {
  convertEm,
  convertRem,
};
