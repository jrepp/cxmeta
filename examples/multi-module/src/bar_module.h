#pragma once
#ifndef _bar_module_h
#define _bar_module_h

//
// Sometimes you want to put some extra text at the top of
// the page to give people some context because bar is
// in fact much harder to understand than foo
//

// Bar is really different from foo and some say much
// harder to understand. It takes no parameters.
//
// * Bar is so very important to proper functionality
// * Some people believe you can implement foo with bar
void bar_function_1(void);

/****
 * bar 2 is actually simpler than foo and bar 1
 *
 * It was documented in this other style because testing
 * is important and we like to format our comments slightly
 * differently based on our preferences.
 */
void bar_function_2(void);

#define // _bar_module_h
