const selectorAll = e =>  document.querySelectorAll( e);
const selector = e => document.querySelector(e);

const nav = selector('.nav');
const mobMenu = selector('.mob-menu');

let isOpen = false;
let isNavOpen = false;

mobMenu.addEventListener('click', function(){

    if( isNavOpen ){
        gsap.to( nav, {
            opacity: 0,
            height: 0,
            duration: 0.5
        } )

        gsap.to( '.nav-link',{
            opacity: 0,
            duration: 0,
        } )

        isNavOpen = !isNavOpen;
    }else{
        gsap.to( nav, {
            opacity: 1,
            height: 'auto',
            duration: 0.5
        } )

        gsap.to( '.nav-link',{
            opacity: 1,
            duration: 0.5
        } )

        isNavOpen = !isNavOpen;
    }
})

function open( e ){
    gsap.to( e, {
        opacity: 1,
        height: 'auto',
        duration: 0.5
    } )
    isOpen = true;
}

function close( e ){
    gsap.to( e, {
        opacity: 0,
        height: 0,
        duration: 0.5
    } )
    isOpen = false;
}
