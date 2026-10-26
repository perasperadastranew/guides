// Рентген экрана: инструменты выключаются по одному, разбор под макетом
(function(){
  const xr=document.getElementById('xr'),out=document.getElementById('xr-out');
  if(!xr||!out)return;
  const tools=[...document.querySelectorAll('#xr-tools button')];
  const devs=[...document.querySelectorAll('#xr-dev button')];
  const T={
    type:['Типографика выключена','Заголовок, текст и цены одного размера. Глазу не за что зацепиться, непонятно, что читать первым.'],
    color:['Цвет выключен','Экран всё ещё читается: иерархию держат размер и композиция. Но пропало настроение «живого» магазина, а главная кнопка стала почти как вторая.'],
    comp:['Композиция выключена','Элементы стоят где попало и с одинаковыми отступами. Группы слиплись, взгляд не понимает, откуда начать и куда идти.'],
    ui:['UI-элементы выключены','Кнопки превратились в текст, карточки потеряли границы. Непонятно, что здесь нажимается.'],
    icons:['Иконки выключены','Корзину приходится искать глазами, а в карточках пропал быстрый маркер, который помогал выбрать.']
  };
  function render(){
    const off=tools.filter(b=>b.getAttribute('aria-pressed')!=='true').map(b=>b.dataset.tool);
    Object.keys(T).forEach(k=>xr.classList.toggle('no-'+k,off.includes(k)));
    const mob=xr.classList.contains('mob');
    out.innerHTML='';
    const add=(h,t)=>{const p=document.createElement('p');const b=document.createElement('b');b.textContent=h+'. ';p.append(b,t);out.append(p)};
    if(!off.length)add('Все инструменты работают','Сначала видно заголовок, потом фото и главную кнопку, ниже — три понятные карточки. Выключи любой инструмент и посмотри, что изменится.');
    off.forEach(k=>add(T[k][0],T[k][1]));
    if(mob)add('Телефон','Структура перестроилась: одна колонка, меню ушло в бургер, кнопки на всю ширину. Это и есть адаптив — блоки меняют порядок, а не уменьшаются.');
  }
  tools.forEach(b=>b.addEventListener('click',()=>{b.setAttribute('aria-pressed',b.getAttribute('aria-pressed')==='true'?'false':'true');render()}));
  devs.forEach(b=>b.addEventListener('click',()=>{devs.forEach(x=>x.setAttribute('aria-pressed',x===b?'true':'false'));xr.classList.toggle('mob',b.dataset.dev==='mob');render()}));
  render();
})();
